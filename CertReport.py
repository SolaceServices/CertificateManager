from CertToolBase import CertToolBase
from SolaceCloudAPI import SolaceCloudAPI

class CertReport(CertToolBase):
  def __init__(self):
    super().__init__()

  def innerMain(self):
    print("Fetching all certs for the broker with service id '" + self.service + "' through the Solace Home Cloud API...")
    certs = self.solaceCloudAPI.getAllCertificates(self.service)
    print(str(len(certs)) + " certificates found on service " + self.service)
    index = 1
    for cert in certs:
      print("\nCertificate #" + str(index) + ":------------------------")
      print("type:" + cert.certType)
      print("cn:" + cert.cn)
      print("expiry:" + cert.expiry)
      print("installed:" + str(cert.installed))
      index = index + 1
    print("----------------------------------------")

if __name__ == "__main__":
  test = CertReport()
  test.main()
