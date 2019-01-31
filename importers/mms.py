from .base import Importer
import requests
from subprocess import call
import time
import os.path


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
        self.force_rs = kwargs.get('force_rs')

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
            # print("Drupal site returned non-200 status: {}".format(res.json()))

            if res.status_code == requests.codes.forbidden:
                self._log('debug',
                          'Forbidden response from POST to server. Likely the cookie is expired, ' +
                          'so the script will exit.')
                exit()

            return False

        else:
            # If everything went OK (200)
            self.res = res.json()

            if self.res and 'status' in self.res.keys():
                if self.res['status'] == '200':
                    self._log('info', '200 status returned from POST for ID {}. Payload: {}.'.format(
                        self.id,
                        self.res
                    ))
                    return True
                else:
                    self._log('info', 'Response from Server with Non-200 Status for ID {}: {} ({})'.format(
                        self.id,
                        self.res['message'],
                        self.res['status']
                    ))
                    if self.res['status'] == '401':
                        raise Exception('Authorization required for posting to server. Check your cookie!')
                    else:
                        return False
            else:
                self._log('warn', "No response from server for ID {}".format(self.id))
                return False

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

    def _get_rsync(self, i3fid, mmsid):

        mmsid = str(mmsid).zfill(5)
        mmspath = mmsid[0:1].zfill(4) + '/' + mmsid[1:].zfill(4)
        srcimg = self.IIIF_LOC + 'prod/' + mmspath + '.jp2'
        destimg = self.IIIF_LOC + self.dest + '/' + i3fid + '.jp2'
        cmd = "rsync -ah --progress {} {}\n".format(srcimg, destimg)
        return cmd

    @staticmethod
    def build_rsync(mid):
        info_url = 'https://images.shanti.virginia.edu/api/imginfo/mmsid/'
        mydest = 'prod'
        strmid = str(mid)
        url = info_url + strmid
        # print("Calling: {}".format(url))
        try:
            indoc = requests.get(url, verify=False)
            if indoc and indoc.json():
                jdata = indoc.json()
                newimgnm = jdata.get('i3fid')
                folder = strmid[0:1].zfill(4)
                imgnm = strmid[1:].zfill(4)
                mysource = "~/Shares/iiif-live/shanti/prod/{}/{}.jp2".format(folder, imgnm)
                mydest = "~/Shares/iiif-live/shanti/{}/{}.jp2".format(mydest, newimgnm)
                mycmd = "rsync -ah --progress {} {}\n".format(mysource, mydest)
                return mycmd
        except requests.exceptions.RequestException as e:
            print("Connection could not be made for {}".format(url))
            return False

    def _exec_cmds(self, cmd, verbose=False):
        if self.rsync == 'auto':
            if verbose:
                print("Executing Cmd: \n{}".format(cmd))
            call(cmd, shell=True)
        elif cmd is not None:
            with open(self.out_path, 'a') as outf:
                outf.write(cmd)
        else:
            print("No command created for rsyncing!")

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
        probs = []
        # If a list of IDs are given
        try:
            for id in id_list:
                self.id = str(id)
                try:
                    if self._already_imported():
                        print("Id {} is already imported.".format(self.id))
                        skipct += 1
                        if self.force_rs:
                            rsync_cmds.append(self.build_rsync(self.id))
                    else:
                        print("Importing metadata for {} into {}".format(self.id, self.base))
                        success = self._import_metadata()
                        if success:
                            impct += 1
                            rsync_cmds.append(self.build_rsync(self.id))
                        else:
                            probs.append(self.id)

                except requests.exceptions.RequestException as e:
                    print("Unable to connect to MMS server for {}: {}".format(self.id, e))
                    probs.append(str(id))

        finally:
            # Only writes Rsync commands for records imported.
            # To recreate missed rsync commands, use the recover-mms-rsync.py script
            if self.rsync == 'file' and len(rsync_cmds) > 0:
                print("Creating Rsync commands ....")
                if os.path.exists(self.out_path):
                    answer = input("The outfile {} already exists. Write over it? ".format(self.out_path))
                    if answer != 'y':
                        return

                with open(self.out_path, 'w') as outf:
                    for rcmd in rsync_cmds:
                        outf.write("{}".format(rcmd))

        endtm = time.time()
        timedelta = endtm - sttm
        print("{} file imported.".format(impct))
        print("{} were skipped because already imported.".format(skipct))
        print("{} imports had problems. Check log for details.".format(len(probs)))
        print("There were problems with the following MMSIDs: {}".format(', '. join(probs)))
        m, s = divmod(timedelta, 60)
        h, m = divmod(m, 60)
        print("Time elapsed: %d hrs %02d mins %02d secs" % (h, m, s))


