import sys
import subprocess
import os

if len(sys.argv) > 1:
    fpath = sys.argv[1]
    print("File path is: {}".format(fpath))
    with open(fpath, 'r') as inf:
        for ln in inf:
            print(ln)
            try:
                mid = int(ln.strip())
                cmd = "python import.py -coll 346 -i {}".format(mid)
                os.system(cmd)
                # subprocess.call(cmd, Shell=True)

            except Exception as e:
                print("Exception: {}".format(e))

            print("--------------------\n")