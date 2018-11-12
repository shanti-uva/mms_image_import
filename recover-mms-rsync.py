
import argparse
import requests
import time
from subprocess import call
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Disable the warning about not checking the https certificate
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

parser = argparse.ArgumentParser(description='Recover MMS rsync commands for a Mandala Images site')
parser.add_argument('-dm', '--domain', default='images.dd:8443',
                    help='What images domain')
parser.add_argument('-ds', '--dest', choices=['test', 'prod'], default='test',
                    help='The start ID')
parser.add_argument('-st', '--start', required=True,
                    help='The start ID')
parser.add_argument('-en', '--end',
                    help='The end ID')
parser.add_argument('-a', '--auto', default=False,
                    help='Whether to automatically perform rsyncs')
parser.add_argument('-o', '--out',
                    help='The end ID')
args = parser.parse_args()


def build_rsync(info_url, mid, mydest):
    mycmd = False
    strmid = str(mid)
    url = info_url + strmid
    print("Calling: {}".format(url))
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
    api_url = 'https://{}/api/imginfo/mmsid/'.format(args.domain)
    dest = args.dest
    mmsstr = int(args.start)
    mmsend = int(args.end) if args.end else mmsstr
    auto = args.auto
    ts = int(time.time())
    outurl = args.out if args.out else '../mms-rsync-{}-{}-{}-{}.sh'.format(
        args.domain.replace('.', '-').replace(':', '_'), mmsstr, mmsend, ts)

    print("\nCreating commands for mms ids: {0} to {1}".format(mmsstr, mmsend))

    for mmsid in range(mmsstr, mmsend + 1):  # range(38049, 38536):
        print("\rDoing: {0}        ".format(mmsid),)
        cmd = build_rsync(api_url, mmsid, dest)

        if auto:
            print("command: {}".format(cmd))
            call(cmd, shell=True)
        else:
            with open(outurl, 'a') as outfile:
                outfile.write(cmd)

    if auto:
        distribute(dest, True)

print("Done")

