import argparse
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from importers import mms
import time
import os

# Disable the warning about not checking the https certificate
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

parser = argparse.ArgumentParser(description='Import images from other apps',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('id', type=str, nargs='+',
                    help='The id number of the record to import')
parser.add_argument('-t', '--type', choices=['MMS', 'Other'], default='MMS',
                    help='What type of image is being imported')
parser.add_argument('-c', '--cookie',
                    help='The Cookie header to pass to the Drupal server.')
parser.add_argument('-hm', '--home', default='https://images.shanti.virginia.edu',
                    help='The host domain name')
parser.add_argument('-d', '--dest', choices=['test', 'prod'], default='prod',
                    help='The IIIF host defaults to "prod"')
parser.add_argument('-src', '--source', choices=['dev', 'stage', 'prod'], default='prod',
                    help='The MMS source for metadata')
parser.add_argument('-rs', '--rsync', choices=['auto', 'file', 'none'], default='file',
                    help='Whether or not to rsync the image file automatically or produce a bash script to do so')
parser.add_argument('-rsf', '--rsyncforce',
                    help='Write rsync commands for all ids even if already imported', action="store_true")
parser.add_argument('-o', '--out_path',
                    help='Path for the output file if sync is false')
parser.add_argument('-p', '--photographer', default='Unknown',
                    help='Default photographer to assign the image record')
parser.add_argument('-coll', '--collection',
                    help='ID of collection to which the record should be assigned')
parser.add_argument('-l', '--logfile',
                    help='Log progress to a file.')
parser.add_argument('-v', '--verbose', default=False, action='store_true',
                    help='Prints progress to stdout.')
args = parser.parse_args()

if __name__ == '__main__':

    # Test image IDs that exist: 67074, 44300-44400, 55000-60000
    # Not found or not images: 19165, 31229, 1795 (av), 645, 67074 (article)
    # Local python text collection: 619207

    # Get the authentication cookie from args or from a file not stored in git
    if args.cookie:
        cookie = args.cookie
    else:
        with open('cookie.txt', 'r') as cookiefile:
            cookie = cookiefile.read()

        if not cookie or cookie == '':
            print("No authentication cookie given. Cannot proceed with import.")
            exit(0)

    if args.rsync == 'file':
        if args.out_path:
            if os.path.exists(args.out_path):
                print("The outpath you have chosen, {}, already exists. Rsync commands will be appende to it")
            # fct = 1
            # while os.path.exists(args.out_path):
            #     resp = input("The rsync file {} already exists. Do you want to write over it (y/n/q)? ".format(args.out_path))
            #     if resp == 'y':
            #         os.remove(args.out_path)
            #     elif resp == 'n':
            #         pts = args.out_path.split('.')
            #         lstptnm = len(pts) - 2
            #         oldpt = '_{}'.format(fct)
            #         if pts[lstptnm].endswith(oldpt):
            #             fct += 1
            #             newpt = '_{}'.format(fct)
            #             pts[lstptnm] = pts[lstptnm].replace(oldpt, newpt)
            #         else:
            #             pts[lstptnm] += '_{}'.format(fct)
            #         args.out_path = '.'.join(pts)
            #     else:
            #         print("Quiting conversions")
            #         exit(0)

    outpath = args.out_path
    if not outpath:
        idstr = args.id if type(args.id) == str else "{}-{}".format(args.id[0], args.id[-1])
        outpath = '../out/mms-import-{}.sh'.format(idstr)

    mylog = args.logfile
    if not mylog:
        tm = int(time.time())
        if type(args.id) == str:
            pts = args.id.split('-')
            idstr = "{}-{}".format(pts[0], pts[-1])
        else:
            idstr = "{}-{}".format(args.id[0], args.id[-1])
        mylog = '../logs/mms-import-{}-{}.log'.format(idstr, tm)
        print("Log file is at: {}".format(mylog))
    if args.type == 'MMS':
        importer = mms.MMSImporter(
            id=','.join(args.id),
            cookie=cookie,
            rsync=args.rsync,
            force_rs=args.rsyncforce,
            out_path=outpath,
            photographer=args.photographer,
            collection=args.collection,
            dest=args.dest,
            source=args.source,
            home=args.home,
            logfile=mylog,
            verbose=args.verbose
        )
        importer.run()

        if os.path.exists(outpath):
            os.chmod(outpath, 0o774)
            print("Out rsync commands are at: {}".format(outpath))

    elif args.type == 'Other':
        print("There are no 'other' types of importation at this point")
        pass

