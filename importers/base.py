import logging
import requests
import json

class Importer(object):

    def __init__(self, id, cookie, out_path, photographer, collection, *args, **kwargs):
        print ("id in base init {}".format(id))
        self.id = id
        self.cookie = cookie
        self.out_path = out_path
        self.photographer = photographer
        self.collection = collection
        self.exists_url = kwargs.get('exists_url')
        if not self.exists_url:
            self.exists_url = 'https://mandala.shanti.virginia.edu'
        if self.exists_url[-1] != '/':
            self.exists_url += '/'
        self.logfile = kwargs.get('logfile')
        if self.logfile:
            logging.basicConfig(filename=self.logfile, level=logging.INFO)
        self.verbose = kwargs.get('verbose', False)
        self.convert = kwargs.get('convert', True)

    def _log(self, level, msg):
        if self.verbose:
            print(msg)

        if self.logfile:
            if level not in ('info', 'debug', 'warning'):
                return
            else:
                getattr(logging, level)(msg)
        else:
            print("No self log file")

    def _already_imported(self):
        url = self.exists_url + str(self.id)
        print ("Self exists url is: {}".format(url))
        res = requests.get(url, verify=False)
        if res.status_code == requests.codes.ok:
            try:
                res_json = res.json()
            except json.decoder.JSONDecodeError as e:
                self._log('warning', 'Item {} skipped because of non-json response body from GET. Response: {}'.format(self.id, res.text))
                return True
            if res_json['nid']:
                self._log('info', 'Item ID {} skipped because it has already been imported.'.format(self.id))
                return True

        return False

    def _import_metadata(self, filepath):
        pass

    def _transfer_image(self):
        pass

    def run(self):
        if self._already_imported():
            print("Already imported")
        else:
            print("not already imported")
        pass


if __name__ == '__main__':
    imptr = Importer(
        id=10001,
        cookie='SSESS36f1ec5e317e53e9ac5cbb2d1be94812:W8xbfgOj3Rns9ZoqIiLbB-B4ZSEgM-ahpe2zMjYVxiI',
        exists_url='https://images-stage.dd:8443/api/imginfo/mmsid/',
        out_path='../out',
        photographer='',
        collection='',
        logfile='../logs/mmstest.log'
    )

    imptr.run()

