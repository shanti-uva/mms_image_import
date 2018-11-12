from .base import Importer
import requests
import json


class MMSImporter(Importer):

    def __init__(self, id, cookie, out_path=None, photographer='Unknown', collection=None, *args, **kwargs):
        self.base = kwargs.get('home')
        self.source = kwargs.get('source')
        self.dest = kwargs.get('dest')
        super().__init__(
            id=id,
            cookie=cookie,
            out_path=out_path,
            photographer=photographer,
            collection=collection,
            exists_url=self.base + '/api/imginfo/mmsid/',
            *args,
            **kwargs
        )
        # self.rsync = True if kwargs.get('rsync') == 'true' else False

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
        print(res.json())
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
            self._log('info', '200 status returned from POST for ID {}. Payload: {}.'.format(
                self.id,
                res.json()
            ))

    def run(self):
        if self._already_imported():
            print("Id {} is already imported.".format(self.id))
        else:
            self._import_metadata()

