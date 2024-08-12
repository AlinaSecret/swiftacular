from cpmapi import PM_TYPE_U64, PM_INDOM_NULL, PM_SEM_INSTANT
import cpmapi
from pcp.pmapi import pmUnits, pmContext
from pcp.pmda import PMDA, pmdaMetric, pmdaInstid, pmdaIndom
import subprocess


kbyteUnits = pmUnits(1, 0, 0, cpmapi.PM_SPACE_KBYTE, 0, 0)

def get_dbs():
    command = [
        'find', '/', '-type', 'f',
        '(', '-name', '*.sqlite', '-o', '-name', '*.db', '-o', '-name', '*.sqlite3', ')'
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print()
    return stdout.splitlines()

class EtcdPMDA(PMDA):

    def __init__(self, name, domain):
        super().__init__(name, domain)

        self.add_metric(name + '.size', pmdaMetric(
            PMDA.pmid(0, 0),
            PM_TYPE_U64,
            PM_INDOM_NULL,
            PM_SEM_INSTANT,
            kbyteUnits
        ))

        self.set_fetch_callback(self.fetch_callback)
        self.set_user(pmContext.pmGetConfig('PCP_USER'))

    # item is id of metric is this pdma as set in add metric fucntion
    def fetch_callback(self, cluster, item, inst):

        return [100, 1] # return result and 1 for sucsees 0 for failure


if __name__ == '__main__':
    EtcdPMDA('swiftdbinfo', 400).run()