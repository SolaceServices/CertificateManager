from SolaceCloudAPI import SolaceCloudAPI
from Logger import Logger
import argparse
from os.path import exists

class CertToolBase:
  def __init__(self):
    versionText = self.loadFile("version.txt")
    versionText = versionText.strip()
    self.version = versionText

    self.logger = Logger("CertificateTool")
    self.logPrint("Runing CertificateTool version " + self.version )

    parser = argparse.ArgumentParser()  
    parser.add_argument('--service',dest='service', required=True, help='The service Id to install the cert')
    parser.add_argument('--token',dest='tokenFile', required=True, help='The file containing the Solace Cloud token')
    self.populateArgsParserWithSpecifics(parser)
    self.args = parser.parse_args()
    
    self.service = self.args.service
    self.logPrint("Acting on Solace Cloud Service " + self.service)

    self.token = self.loadFile(self.args.tokenFile)
    if len(self.token) > 0:
      self.logPrint("Token file found and loaded.")
    else:
      raise RuntimeError("No token found, cannot proceed.")
    
    self.solaceCloudAPI = SolaceCloudAPI(self.token, self.logger, dict())

  def logPrint(self, txt: str):
    self.logger.log(txt)
    print(txt)

  def populateArgsParserWithSpecifics(self, parser: argparse.ArgumentParser):
    # child class overrides
    pass

  def loadFile(self, pathToFile: str) -> str:
    file_exists = exists(pathToFile)
    if not file_exists:
        raise FileNotFoundError("Cannot find the '" + pathToFile + ". Is this the correct path?")
    fileObject = open(pathToFile)
    fileContents = fileObject.read().rstrip()
    fileObject.close()
    return fileContents

  def innerMain(self):
    self.logPrint("This file has no main program")

  def main(self):
    self.innerMain()
    self.logPrint("Tool completed sucessfully.")

