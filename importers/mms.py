from . import base

class MMSImporter(base.Importer):

    def __init__(self, id, cookie, out_path=None, photographer=None, collection=None, *args, **kwargs):
        self.base = kwargs.get('home')
        print("id in mms importer obj: {}".format(id))
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
        print ("after init: {}".format(self.id))
        #self.dest = 'prod' if kwargs.get('dest') == 'prod' else 'test'
        #self.rsync = True if kwargs.get('rsync') == 'true' else False

    def run(self):
        print("self id in run: {}".format(self.id))
        if self._already_imported():
            print("imported: {}").format(self.id)
        else:
            headers = {
                'Cookie': self.cookie
            }
            print("Not imported: {}").format(self.id)


