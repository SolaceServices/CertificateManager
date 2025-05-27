from CertToolBase import CertToolBase
from RestfulAPI import RestfulAPI
from SolaceCloudAPI import SolaceCloudAPI
from Logger import Logger
from os.path import exists

class CertReport(CertToolBase):
  def __init__(self):
    super().__init__()

  def innerMain(self):
    print("Deleting any uninstalled custom certificates for the broker with service id '" + self.service + "' through the Solace Home Cloud API...")

    finished = False
    deleteCount = 0
    while not finished:
      cert = self.solaceCloudAPI.getCustomCertificate (self.service)
      if not cert == None:
        self.solaceCloudAPI.deleteCertificate(self.service, cert.certificateId)
        deleteCount = deleteCount + 1
      else:
        finished = True

    print(str(deleteCount) + " certificates were deleted on service " + self.service)
    print("----------------------------------------")

if __name__ == "__main__":
  test = CertReport()
  test.main()
