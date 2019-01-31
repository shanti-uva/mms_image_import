import argparse
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import time
import datetime

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
    try:
        res = requests.get(path, verify=False)
        if res.status_code == requests.codes.ok:
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


def mms_check(mmsid):
    mmsurl = 'http://mms.thlib.org/media_objects/{}.json'.format(mmsid)
    # print(mmsurl)
    mmsres = do_request(mmsurl)
    # print(type(mmsres))
    if not mmsres or not isinstance(mmsres, dict) or ('status' in mmsres and mmsres['status'] == '404'):
        return "404"
    else:
        # print("here")
        kys = list(mmsres.keys())
        return kys[0]


def concat_list(alist):
    newlist = []
    st = False
    last = False
    try:
        for item in alist:
            item = int(item)
            if not st:
                st = item
                last = item
            elif item == last + 1:
                last = item
            else:
                if last == st:
                    newlist.append(str(st))
                elif last == st + 1:
                    newlist.append(str(st))
                    newlist.append(str(last))
                else:
                    rngstr = "{}-{}".format(st, last)
                    newlist.append(rngstr)
                st = item
                last = item

    except ValueError as ve:
        pass

    return newlist

def get_current_timestamp():
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return timestamp


def do_checks(allids):
    '''
    Checks the list of mms ids to see if they are imported. First, checks if it's an image in mms
    Then if it is, it checks whether its been imported and whether the image has been uploaded
    :param allids:
    :return:
    '''
    if len(ids) > 3:
        idstr = '_'.join(ids[0:3])
    else:
        idstr = '_'.join(ids)

    outfile = '../checks/imgcheck_' + args.type + '_' + idstr + '.csv' if not args.output else args.output
    print("Outfile location: {}".format(outfile))
    with open(outfile, 'w') as outf:
        outf.write('"Mmsid","Type","Imported","Uploaded","Modified","Created"' + "\n")
        cts = get_current_timestamp()
        for iid in allids:
            print("\rDoing mms id {} ....      ".format(iid), end=" ")
            iid = str(iid)
            mmstype = mms_check(iid)
            imp = 0
            upl = 0
            if mmstype == 'picture':
                status = check_id(iid)
                if status == 1:
                    imp = 1
                    upl = 1

                elif status == 2:
                    imp = 1
                    upl = 0

            outf.write('{},"{}",{},{},"{}","{}"'.format(iid, mmstype, imp, upl, cts, cts) + "\n")

            # except Exception as e:
            #    print("\rThere was an exception during {}:{}".format(iid, e.),)



if __name__ == '__main__':

    if args.id:
        sttm = time.time()
        ids = args.id
        idlist = []
        for idstr in ids:
            idlist += parse_id_string(idstr)

        if debug:
            print("id in: ", args.id)
            print("The list is: ", idlist)

        do_checks(idlist)

        endtm = time.time()
        timedelta = endtm - sttm
        m, s = divmod(timedelta, 60)
        h, m = divmod(m, 60)
        print("Time elapsed: %d hrs %02d mins %02d secs" % (h, m, s))
        print("The Checking is Done!")

    else:
        print("No ids given. Nothing to check! Bye!")