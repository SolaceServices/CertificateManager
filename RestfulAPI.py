import requests
import json
import math
from enum import Enum
from os.path import exists

class RestfulOperations(Enum):
    Create = 0
    Update = 1
    Delete = 2

class AlreadyExistsException(Exception):
    """ custom exception class """

class RestfulAPI():
  def __init__(self, shouldVerify: bool):
    self.verify = shouldVerify

  def loadJsonTemplate(self, templateFileName: str) -> dict:
    file_exists = exists(templateFileName)
    if not file_exists:
        raise FileNotFoundError("Cannot find the " + templateFileName + " file")

    fileObject = open(templateFileName)
    fileContents = fileObject.read()
    fileObject.close()
    return fileContents
  
  def logPrint(self, txt: str):
    self.logger.log(txt)
    #print(txt)

  def handleResponse(self, response: requests.Response):
    self.logPrint("Http response code=" + str(response.status_code))
    self.logPrint("response=" + response.text)
    self.logger.addSeperator()
    
    responseFamily = round(response.status_code, -2)
    
    if not responseFamily == 200:
        jsonResponse = json.loads(response.text)

        if "message" in jsonResponse:
          errorMsg = jsonResponse['message']
          meta = str(jsonResponse['meta'])
          if "already exists" in meta:
              raise AlreadyExistsException("http error: " + str(response.status_code))
          else:
              raise RuntimeError("http error: " + str(response.status_code) + " (" + errorMsg + ")")
        else:
          if "error" in response:
            errorMsg = jsonResponse['error']
            raise RuntimeError("http error: " + str(response.status_code) + " (" + errorMsg + ")")

  def post(self, actionDesc: str, url: str, body: str) -> str:
    self.logPrint(actionDesc + " (POST) on Url=" + url + " with body=" + body)
    self.logPrint("Note: http call made with verify=" + str(self.verify))

    useProxies = False
    if not self.proxies == None:
      if len(self.proxies) > 0:
        useProxies = True      

    if useProxies:
      self.logPrint("using proxies:" + str(self.proxies))
      response = requests.post(url, headers=self.headers, data=body, verify=self.verify, proxies = self.proxies)
    else:
      self.logPrint("no proxies were configured")
      response = requests.post(url, headers=self.headers, data=body, verify=self.verify)

    self.handleResponse(response)
    return response

  def put(self, actionDesc: str, url: str, body: str) -> str:
    self.logPrint(actionDesc + " (PUT) on Url=" + url + " with body=" + body)
    self.logPrint("Note: http call made with verify=self.verify")

    useProxies = False
    if not self.proxies == None:
      if len(self.proxies) > 0:
        useProxies = True      

    if useProxies:
      self.logPrint("using proxies:" + str(self.proxies))
      response = requests.put(url, headers=self.headers, data=body, verify=self.verify, proxies = self.proxies)
    else:
      self.logPrint("no proxies were configured")
      response = requests.put(url, headers=self.headers, data=body, verify=self.verify)

    self.handleResponse(response)
    return response

  def get(self, actionDesc: str, url: str) -> str:
    self.logPrint(actionDesc + " (GET) on Url=" + url)
    self.logPrint("Note: http call made with verify=self.verify")

    useProxies = False
    if not self.proxies == None:
      if len(self.proxies) > 0:
        useProxies = True      

    if useProxies:
      self.logPrint("using proxies:" + str(self.proxies))
      response = requests.get(url, headers=self.headers, verify=self.verify, proxies = self.proxies)
    else:
      self.logPrint("no proxies were configured")
      response = requests.get(url, headers=self.headers, verify=self.verify)
    
    self.handleResponse(response)
    return response

  def delete(self, actionDesc: str, url: str) -> str:
    self.logPrint(actionDesc + " (DELETE) on Url=" + url)
    self.logPrint("Note: http call made with verify=self.verify")
    response = requests.delete(url, headers=self.headers, verify=self.verify)
    self.handleResponse(response)
    return response
