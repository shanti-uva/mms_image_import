import logging
import requests
import json
import http

class Importer(object):

    def __init__(self, id, cookie, out_path, photographer, collection, *args, **kwargs):
        self.id = id
        if '-' in id or ',' in id:
            self.idstr = id
            idtmp = id.replace(' ', '')
            rngs = idtmp.split(',')
            idlist = list()
            for rng in rngs:
                if '-' in rng:
                    rpts = rng.split('-')
                    idlist = idlist + list(range(int(rpts[0]), int(rpts[1]) + 1))
                else:
                    idlist.append(int(rng))
            idlist.sort()
            self.id_list = idlist
        else:
            self.id_list = False
        self.cookie = cookie
        self.out_path = out_path
        self.photographer = photographer
        self.collection = collection

        self.base = kwargs.get('home')
        self.source = kwargs.get('source')
        self.dest = kwargs.get('dest')

        self.exists_url = kwargs.get('exists_url')
        if not self.exists_url:
            self.exists_url = 'https://mandala.shanti.virginia.edu'
        if self.exists_url[0:4] != 'http':
            self.exists_url = self.base + self.exists_url
        if self.exists_url[-1] != '/':
            self.exists_url += '/'

        self.logoff = kwargs.get('logoff')
        if self.logoff and (self.logoff != 'false' or self.logoff != '0' or self.logoff != '-1'):
            self.logoff = True
        else:
            self.logoff = False

        if not self.logoff:
            self.logfile = kwargs.get('logfile')
            if self.logfile:
                logging.basicConfig(filename=self.logfile, level=logging.INFO)
        self.verbose = kwargs.get('verbose', False)
        self.convert = kwargs.get('convert', True)

    def _log(self, level, msg):
        if self.logoff:
            return

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
        self._log('info', "Url in _already_imported (base.py): {}".format(url))
        try:
            res = requests.get(url, verify=False)
            if res.status_code == requests.codes.ok:
                try:
                    res_json = res.json()

                except json.decoder.JSONDecodeError as e:
                    self._log('warning', 'Item {} skipped in _already_imported because of non-json response body from GET. ' +
                              'Response: {}'.format(self.id, res.text))
                    return True

                if 'nid' in res_json.keys():
                    self._log('info', 'Item ID {} skipped because it has already been imported.'.format(self.id))
                    return True
                else:
                    self._log('warning', "JSON response in _already_imported has no nid: {}".format(res_json))
                    return False

        except requests.exceptions.RequestException as e:
            print("Could not find out if already imported!")
            if e:
                print(str(e))
        # except http.HTTPException as htpe:
        #     print("Http Exception")
        #     if htpe:
        #         print(str(htpe))

        return False

    def _import_metadata(self):
        pass

    def _do_rsync(self):
        pass

    def run(self):
        if self._already_imported():
            print("Already imported")
        else:
            print("not already imported")
        pass


if __name__ == '__main__':

    # Disable the warning about not checking the https certificate
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    imptr = Importer(
        id=10001,
        cookie='cookie info',
        exists_url='https://images.dd:8443/api/imginfo/mmsid/',
        out_path='../out',
        photographer='',
        collection='',
        logfile='../logs/mmstest.log'
    )

    imptr.run()

