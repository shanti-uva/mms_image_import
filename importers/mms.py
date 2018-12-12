from .base import Importer
import requests
from subprocess import call
import time


class MMSImporter(Importer):

    MMS_DEV='http://dev-mms.thlib.org/media_objects/'
    MMS_STAGE='http://staging-mms.thlib.org/media_objects/'
    MMS_PROD='http://mms.thlib.org/media_objects/'

    IIIF_LOC='~/Shares/iiif-live/shanti/'

    def __init__(self, id, cookie, out_path=None, photographer='Unknown', collection=None, *args, **kwargs):
        super().__init__(
            id=id,
            cookie=cookie,
            out_path=out_path,
            photographer=photographer,
            collection=collection,
            exists_url='/api/imginfo/mmsid/',
            *args,
            **kwargs
        )
        self.rsync = kwargs.get('rsync')

    def _import_metadata(self):
        import_path = '/admin/shanti_images/import/json/'
        import_url = self.base + import_path + self.id
        headers = {
            'Cookie': self.cookie
        }

        postdata = {
            'mmsid': self.id,
            'source': self.source,
            'publish': True,
            'photographer': self.photographer,
            'coll': self.collection if self.collection else ''
        }
        if self.collection:
            postdata['image_coll_node'] = self.collection
        if self.photographer:
            postdata['default_agent'] = self.photographer

        res = requests.post(import_url, headers=headers, data=postdata, verify=False)

        if res.status_code != requests.codes.ok:
            self._log('warning', 'Non-200 status returned from POST for ID {}. Code was {}.'.format(
                self.id,
                res.status_code
            ))
            if res.status_code == requests.codes.forbidden:
                self._log('debug',
                          'Forbidden response from POST to server. Likely the cookie is expired, ' +
                          'so the script will exit.')
                exit()
        else:
            # If everything went OK (200)
            self.res = res.json()
            self._log('info', '200 status returned from POST for ID {}. Payload: {}.'.format(
                self.id,
                res.json()
            ))

        # res.json() looks like this:
        # {
        #     'mmsid': '44301',
        #     'nid': '619213',
        #     'i3fid': 'shanti-image-loc-295724',
        #     'title': '(Untitled)',
        #     'durl': 'https://images.dd:8443/node/619213',
        #     'mmsurl': 'http://staging-mms.thlib.org/media_objects/44301',
        #     'status': '200',
        #     'msg': 'success'
        # }

    def _get_rsync(self):
        if not hasattr(self, 'res'):
            return
        i3fid = self.res['i3fid']
        mmsid = str(self.res['mmsid']).zfill(5)
        mmspath = mmsid[0:1].zfill(4) + '/' + mmsid[1:].zfill(4)
        srcimg = self.IIIF_LOC + 'prod/' + mmspath + '.jp2'
        destimg = self.IIIF_LOC + self.dest + '/' + i3fid + '.jp2'
        cmd = "rsync -ah --progress {} {}\n".format(srcimg, destimg)
        return cmd

    def _exec_cmds(self, cmd, verbose=False):
        if self.rsync == 'auto':
            if verbose:
                print("Executing Cmd: \n{}".format(cmd))
            call(cmd, shell=True)
        else:
            with open(self.out_path, 'a') as outf:
                outf.write(cmd)

    def _distribute(self, verbose=False):
        url = 'http://fuploadtest.lib.virginia.edu:8091/fupload/distribute'
        if self.dest == 'prod':
            url = url.replace('fuploadtest', 'fupload')
        res = requests.get(url)

        if res.status_code != requests.codes.ok:
            print("Could not distribute file on {}: {} - {]".format(self.dest, res.status_code, res.json()))
        elif verbose:
            print("File distributed on {}: {}".format(self.dest, res.json()))

    def run(self):
        sttm = time.time()
        idtype = "List" if self.id_list else "Individual"
        print("Beginning Import, Type: {}".format(idtype))
        id_list = self.id_list if self.id_list else [int(self.id)]
        rsync_cmds = []
        be_verbose = True
        impct = 0
        skipct = 0
        # If a list of IDs are given
        for id in id_list:
            self.id = str(id)
            try:
                if self._already_imported():
                    print("Id {} is already imported.".format(self.id))
                    skipct += 1
                else:
                    print("Importing metadata for {} into {}".format(self.id, self.base))
                    self._import_metadata()
                    rsync_cmds.append(self._get_rsync())
                    impct += 1
            except requests.exceptions.RequestException as e:
                print("Unable to connect to MMS server")

        for rscmd in rsync_cmds:
            self._exec_cmds(rscmd, be_verbose)

        if self.rsync == 'auto':
            self._distribute(be_verbose)

        endtm = time.time()
        timedelta = endtm - sttm
        print("{} file imported. {} files skipped".format(impct, skipct))
        m, s = divmod(timedelta, 60)
        h, m = divmod(m, 60)
        print("Time elapsed: %d hrs %02d mins %02d secs" % (h, m, s))
