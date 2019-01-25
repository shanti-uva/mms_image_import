
import argparse
import requests
import time
import os
from subprocess import call
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Disable the warning about not checking the https certificate
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def build_rsync(info_url, mid, mydest):
    mycmd = False
    strmid = str(mid)
    url = info_url + strmid
    print("Calling: {}".format(url))
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


def distribute(self, mydest='test', verbose=False):
    url = 'http://fuploadtest.lib.virginia.edu:8091/fupload/distribute'
    if mydest == 'prod':
        url = url.replace('fuploadtest', 'fupload')
    res = requests.get(url)

    if res.status_code != requests.codes.ok:
        print("Could not distribute file on {}: {} - {]".format(mydest, res.status_code, res.json()))
    elif verbose:
        print("File distributed on {}: {}".format(mydest, res.json()))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Recover MMS rsync commands for a Mandala Images site',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-dm', '--domain', default='images.shanti.virginia.edu',
                        help='What images domain')
    parser.add_argument('-ds', '--dest', choices=['test', 'prod'], default='prod',
                        help='Destination or the IIIF Server to which to copy the mms image')
    parser.add_argument('-i', '--ids', required=True,
                        help='The range of IDs or single ID to create the commands for')
    parser.add_argument('-a', '--auto', default=False,
                        help='Whether to automatically perform rsyncs')
    parser.add_argument('-o', '--outdir', default='../out',
                        help='The out directory')
    args = parser.parse_args()

    api_url = 'https://{}/api/imginfo/mmsid/'.format(args.domain)
    dest = args.dest
    mmsids = args.ids.split('-')
    mmsstr = int(mmsids[0])
    if len(mmsids) == 1:
        mmsend = mmsstr + 1
    else:
        mmsend = int(mmsids[1]) + 1
    auto = args.auto
    ts = int(time.time())
    rpst = ''
    if 'test' not in args.domain and 'dev' not in args.domain:
        rpst = 'prod'
    domabbr = args.domain.replace('shanti.virginia.edu', rpst).replace('.', '-')
    outurl = '{}/mms-rsync-{}-{}-{}-{}.sh'.format(
        args.outdir,
        domabbr,
        mmsstr,
        (mmsend - 1),
        ts)

    if os.path.exists(outurl):
        res = input("The outpath {} exists. Do you want to write over it? (y | n): ")
        if res != 'y':
            print("Exiting script!")
            exit(0)

    print("\nCreating commands for mms ids: {0} to {1}".format(mmsstr, mmsend - 1))

    badids = []

    for mmsid in range(mmsstr, mmsend):  # range(38049, 38536):
        # print("\rDoing: {0}        ".format(mmsid),)
        cmd = build_rsync(api_url, mmsid, dest)

        if auto:
            print("command: {}".format(cmd))
            call(cmd, shell=True)
        elif cmd:
            with open(outurl, 'a') as outfile:
                outfile.write(cmd)
        else:
            print("Unable to get info for MSSID {}".format(mmsid))
            badids.append(str(mmsid))

    if auto:
        distribute(dest, True)

if os.path.isfile(outurl):
    os.chmod(outurl, 0o774)
    print("Done! Commands written to: {}".format(outurl))
else:
    print("No commands written!")

if len(badids) > 0:
    print("The information for the following IDs could not be accessed: {}".format(', '.join(badids)))

