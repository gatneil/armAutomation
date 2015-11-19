import argparse
import time
import subprocess
import sys
import shlex

WAIT_SEC = 10

parser = argparse.ArgumentParser()
parser.add_argument('--prefix', required=True)
args = parser.parse_args()

rgname = args.prefix + "rg"
depname = args.prefix + "dep"

params = '{"uniqueNamePrefix":{"value":"' + args.prefix + '"},"instanceCount":{"value":"20"},"adminUsername":{"value":"ubuntu"},"adminPassword":{"value":"P4$$w0rd"}}'

deployCommand = ['azure', 'group', 'create', rgname, 'West US', '-d', depname, '-f', 'wait.json', '-p', params]
checkCommand = ['azure', 'group', 'deployment', 'show', rgname, depname]
logCommand = ['azure', 'group', 'log', 'show', rgname, '--all']
destroyCommand = ['azure', 'group', 'delete', '-q', rgname]

numFailures = 0
while True:
    start = time.time()
    res = subprocess.check_output(deployCommand).strip()

    provisioningResult = ""
    end = None

    while end == None:
        time.sleep(WAIT_SEC)
        try:
            res = subprocess.check_output(checkCommand).strip()
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
                    logOutput = subprocess.check_output(logCommand, stderr=subprocess.STDOUT).strip()
                    with open(args.prefix + 'FailureLog' + str(numFailures), 'w') as logfile:
                        logfile.write(logOutput)

                    numFailures += 1
                    

            
    delta = end - start

    print(provisioningResult + ": " + str(delta))
    sys.stdout.flush()

    deleted = False

    while True:
        try:
            time.sleep(WAIT_SEC)
            res = subprocess.check_output(destroyCommand, stderr=subprocess.STDOUT).strip()
            break
        except Exception as e:
            continue

    while not deleted:
        time.sleep(WAIT_SEC)
        try:
            res = subprocess.check_output(checkCommand, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            if "could not be found" in str(e.output):
                deleted = True
