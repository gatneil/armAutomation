import argparse
import time
import subprocess
import sys

WAIT_SEC = 10

parser = argparse.ArgumentParser()
parser.add_argument('--deployfile', required=True)
parser.add_argument('--checkfile', required=True)
parser.add_argument('--destroyfile', required=True)
args = parser.parse_args()

while True:
    start = time.time()
    res = subprocess.check_output(["sh", args.deployfile]).strip()

    provisioningResult = ""
    end = None

    while end == None:
        time.sleep(WAIT_SEC)
        try:
            res = subprocess.check_output(["sh", args.checkfile]).strip()
        except Exception as e:
            continue

        for line in res.split('\n'):
            if "ProvisioningState" in line:
                if "Succeeded" in line:
                    provisioningResult = "Successful"
                    end = time.time()
                elif "Failed" in line:
                    provisioningResult = "Failed"
                    end = time.time()

            
    delta = end - start

    print(provisioningResult + ": " + str(delta))
    sys.stdout.flush()

    deleted = False

    while True:
        try:
            time.sleep(WAIT_SEC)
            res = subprocess.check_output(["sh", args.destroyfile], stderr=subprocess.STDOUT).strip()
            break
        except Exception as e:
            continue

    while not deleted:
        time.sleep(WAIT_SEC)
        try:
            res = subprocess.check_output(["sh", args.checkfile], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            if "could not be found" in str(e.output):
                deleted = True
