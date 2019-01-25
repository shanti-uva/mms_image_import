import argparse
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import time
import os

debug = False

# Disable the warning about not checking the https certificate
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

parser = argparse.ArgumentParser(description='Check that Images have been imported',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('id', type=str, nargs='+',
                    help='The id number(s) of the record to check')
parser.add_argument('-t', '--type', choices=['mmsid', 'nid', 'siid'], default='mmsid',
                    help='What type of id is being given')
parser.add_argument('-d', '--domain', default='https://images.shanti.virginia.edu',
                    help='The host domain name checking against')
parser.add_argument('-o', '--output',
                    help='Filename to print results to. If not given, results appear only on screen')
args = parser.parse_args()


def parse_id_string(idstr):
    idlist = []
    if idstr is None or not isinstance(idstr, str):
        if debug:
            print("Insufficient ID string provided!")
        return idlist

    chunks = idstr.replace(' ', '').split(',')
    for chk in chunks:
        parts = chk.split('-')
        if len(parts) == 2:
            idlist += list(range(int(parts[0]), int(parts[1]) + 1))
        else:
            idlist.append(int(parts[0]))

    return idlist


def do_request(path):
    res = requests.get(path, verify=False)
    if res.status_code == requests.codes.ok:
        try:
            res_json = res.json()
            return res_json
        except Exception as e:
            pass
    return False


def check_id(myiid):
    myiid = str(myiid)
    path = args.domain + '/api/imginfo/' + args.type + '/' + myiid
    if debug:
        print("path: " + path)
    imgdata = do_request(path)

    if imgdata:
        imgurl = imgdata['image_url']
        imgurl = imgurl.split('/full')
        imgurl = imgurl[0] + '/info.json'
        iiifdata = do_request(imgurl)
        # print(type(iiifdata), iiifdata)
        if iiifdata and 'profile' in iiifdata:
            return 1
        else:
            return 2
    return 3


if __name__ == '__main__':

    if args.id:
        try:
            ids = args.id
            allids = []
            done = []
            notup = []
            notimp = []
            for idstr in ids:
                allids += parse_id_string(idstr)

            if debug:
                print("id in: ", args.id)
                print("The list is: ", allids)

            sttm = time.time()

            for iid in allids:
                iid = str(iid)
                status = check_id(iid)
                if status == 1:
                    print("\r{} {} has ALREADY been imported and uploaded                     ".format(args.type, iid), end=" ")
                    done.append(iid)
                elif status == 2:
                    print("\r{} {} has been imported but NOT yet been uploaded              ".format(args.type, iid), end=" ")
                    notup.append(iid)
                else:
                    print("\r{} {} has not been imported at all                         ".format(args.type, iid), end=" ")
                    notimp.append(iid)

        finally:
            ts = time.time()
            idstr = ''
            if len(ids) > 3:
                idstr = '_'.join(ids[0:3])
            else:
                idstr='_'.join(ids)

            outfile = '../checks/imgcheck_' + args.type + '_' + idstr + '.data' if not args.output else args.output

            with open(outfile, 'w') as outf:
                # Doing not uploaded files
                outf.write("Not Uploaded:\n")
                if len(notup) == 0:
                    outf.write("None\n")
                for itm in notup:
                    outf.write("{}\n".format(itm))

                # Doing not imported MMS Records
                outf.write("\nNot Imported:\n")
                if len(notimp) == 0:
                    outf.write("None\n")
                for itm in notimp:
                    outf.write("{}\n".format(itm))

                # Doing those which are completely done
                outf.write("\nCompletely Done:\n")
                if len(done) == 0:
                    outf.write("None\n")
                for itm in done:
                    outf.write("{}\n".format(itm))

            print("\n{} IDs have been completely done\n".format(len(done)))
            print("{} IDs have imported but the image has not been uploaded\n".format(len(notup)))
            print("{} IDs have have not been imported\n".format(len(notimp)))
            endtm = time.time()
            timedelta = endtm - sttm
            m, s = divmod(timedelta, 60)
            h, m = divmod(m, 60)
            print("Time elapsed: %d hrs %02d mins %02d secs" % (h, m, s))

            print("Now I'm really done!")


