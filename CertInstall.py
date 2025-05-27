from CertToolBase import CertToolBase
from SolaceCloudAPI import SolaceCloudAPI
import argparse

class CertInstall(CertToolBase):
  def __init__(self):
    super().__init__()

  def populateArgsParserWithSpecifics(self, parser: argparse.ArgumentParser):
    parser.add_argument('--cert',dest='certFile', required=True, help='The file containing the certificate')
    parser.add_argument('--key',dest='keyFile', required=True, help='The file containing the certs private key')
    parser.add_argument('--passPhrase',dest='passPhrase', required=True, help='The passPhrase for the private key')

  def prepCert(self, cert: str) -> str:
    certContent = cert.replace("\r", "")
    certContent = certContent.replace("\n", "\\n")
    certContent = certContent.replace("\n\r", "")
    certContent = certContent.replace("\r\n", "")
    return certContent

  def loadCertFile(self, pathToFile: str) -> str:
    body = self.loadFile(pathToFile)
    body = self.prepCert(body)
    return body

  def innerMain(self):
    certBody = self.loadCertFile(self.args.certFile)
    keyBody = self.loadCertFile(self.args.keyFile)

    print("Uploading your certificate " + self.args.certFile + " to the broker with service ID '" + self.service + "' through the Solace Home Cloud (SaS) API...")    
    self.solaceCloudAPI.uploadCertificate(self.service, certBody, keyBody)
    cert = self.solaceCloudAPI.getCustomCertificate(self.service)
    if not cert == None:
      print("Cert was uploaded sucesfully. Installing...")    
      self.solaceCloudAPI.installCertificate(self.service, cert, self.args.passPhrase)

      print("Cert wasinstalled sucesfully. Fetching it to double check...")    
      cert = self.solaceCloudAPI.getCustomCertificate(self.service)
      print("------------------------")
      print("Cert uploaded and installed:")
      print("type:" + cert.certType)
      print("cn:" + cert.cn)
      print("expiry:" + cert.expiry)
      print("installed:" + str(cert.installed))

    else:
      print("INTERNAL ERROR: the cert was uploaded, but is not found when querying Solace Cloud.")

if __name__ == "__main__":
  test = CertInstall()
  test.main()
