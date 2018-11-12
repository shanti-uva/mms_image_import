import argparse
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from importers import mms
import time

# Disable the warning about not checking the https certificate
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

parser = argparse.ArgumentParser(description='Import images from other apps')
parser.add_argument('-t', '--type', choices=['MMS', 'Other'], default='MMS',
                    help='What type of image is being imported')
parser.add_argument('-i', '--id', required=True,
                    help='The id number of the record to import')
parser.add_argument('-c', '--cookie',
                    help='The Cookie header to pass to the Drupal server.')
parser.add_argument('-hm', '--home', default='https://images.dd:8443',
                    help='The host domain name')
parser.add_argument('-d', '--dest', choices=['test', 'prod'], default='test',
                    help='The IIIF host defaults to "test"')
parser.add_argument('-src', '--source', choices=['dev', 'prod'], default='dev',
                    help='The MMS source for metadata')
parser.add_argument('-rs', '--rsync', choices=['auto', 'file'], default='auto',
                    help='Whether or not to rsync the image file automatically or produce a bash script to do so')
parser.add_argument('-o', '--out_path',
                    help='Path for the output file if sync is false')
parser.add_argument('-p', '--photographer', default='Unknown',
                    help='Default photographer to assign the image record')
parser.add_argument('-coll', '--collection',
                    help='ID of collection to which the record should be assigned')
parser.add_argument('-l', '--logfile', default='logs/mmsimport-{}.log'.format(time.time()),
                    help='Log progress to a file.')
parser.add_argument('-v', '--verbose', default=False, action='store_true',
                    help='Prints progress to stdout.')
args = parser.parse_args();

if __name__ == '__main__':

    # Test image IDs that exist: 67074, 44300-44400, 55000-60000
    # Not found or not images: 19165, 31229, 1795 (av), 645, 67074 (article)

    # Get the authentication cookie
    if args.cookie:
        cookie = args.cookie
    else:
        with open('cookie.txt', 'r') as cookiefile:
            cookie = cookiefile.read()

        if not cookie or cookie == '':
            print("No authentication cookie given. Cannot proceed with import.")
            exit(0)

    if args.type == 'MMS':
        importer = mms.MMSImporter(
            id=args.id,
            cookie=cookie,
            rsync=args.rsync,
            out_path=args.out_path,
            photographer=args.photographer,
            collection=args.collection,
            dest=args.dest,
            source=args.source,
            home=args.home,
            logfile=args.logfile,
            verbose=args.verbose
        )
        importer.run()
    elif args.type == 'Other':
        print("There are no 'other' types of importation at this point")
        pass

