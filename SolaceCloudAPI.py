#
# Copyright 2025 Solace Corporation
# 
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements. See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership. The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.
import json
import time
import sys
from RestfulAPI import RestfulAPI
from RestfulAPI import RestfulOperations
from RestfulAPI import AlreadyExistsException
from Logger import Logger

checkPostStatusUrl = 'https://api.solace.cloud/api/v0/services/{serviceId}/requests/{requestId}'
uploadCertUrl = "https://api.solace.cloud/api/v2/missionControl/eventBrokerServices/{serviceId}/serverCertificates";

getCertsUrl = "https://api.solace.cloud/api/v2/missionControl/eventBrokerServices/{serviceId}/serverCertificates"
getSingleCertUrl = "https://api.solace.cloud/api/v2/missionControl/eventBrokerServices/{serviceId}/serverCertificates/{certificateId}"
deleteCertUrl = "https://api.solace.cloud/api/v2/missionControl/eventBrokerServices/{serviceId}/serverCertificates/{certificateId}"
operationStatsUrl = "https://api.solace.cloud/api/v2/missionControl/eventBrokerServices/{serviceId}/operations/{operationId}"
installCertUrl = "https://api.solace.cloud/api/v2/missionControl/eventBrokerServices/{serviceId}/serverCertificates/{certificateId}/install"

class SolaceCloudInstalledCert: 
  def __init__(self):
    self.serviceId = ""
    self.certificateId = ""
    self.expiry = ""
    self.cn = ""
    self.installed = ""
    self.certType = ""

class SolaceCloudAPI(RestfulAPI):

    # IMPORTANT: In the header is the Solace Cloud token. Ensure that you create a token in your account that has at least the 
    # following permissions:
    #Create / Update / Delete Client Profiles
    #Create services in your organizationes, Delete My Services, Delete services you created, Get My Services with Management Credentials
  def __init__(self, token, logger: Logger, proxies: dict):
    super().__init__(True)

    self.token = token
    # The headers are used for all the calls here. You don't actually need the Content-type for non payload calls, but it 
    # doesn't hurt anything and keeps it simple. 
    self.headers  = {"Content-Type": "application/json", "Authorization": "Bearer {token}"}
    self.headers['Authorization'] = self.headers['Authorization'].replace("{token}", self.token)
    self.logger = logger
    self.proxies = proxies

    self.logPrint("After initializaton, SC API has " + str(proxies))

  def __waitForRequestToComplete(self, purpose: str, url: str, dataElement: str, waitIntervalInSeconds: int, maxRetries: int) -> str:
    print ("Waiting for service request '" + purpose + "' to complete.", end ="")
    sys.stdout.flush()
    waiting = True
    retries = 0
    while waiting:
        response = super().get(purpose, url)
        #print(response.text)
        #print("get status: ", response.status_code)
        jsonResponse = json.loads(response.text)

        adminProgress = "inProgress"
        try:
            currentStatus = jsonResponse['data'][dataElement]
        except:
            #print("request is not ready to be queried")
            currentStatus = "Unknown"

        if currentStatus == "completed":
            waiting = False
            self.logPrint("The " + purpose + " request has completed")
        elif currentStatus == "failed":
            errorMsg = jsonResponse['data']['error']['message']
            raise RuntimeError(errorMsg)
        else:
            print(".", end="")
            sys.stdout.flush()
            time.sleep(waitIntervalInSeconds)
            retries = retries + 1
            if retries > maxRetries:
                raise Exception("The '" + purpose + "' request has timed out. Pipeline fails.")
  
    return jsonResponse           

  def postAndWait(self, reason: str, service: str, url: str, payload: str):
    response = super().post("install cert", url, payload)
    jsonResponse = json.loads(response.text)
    data = jsonResponse['data']
    id = data['id']
    startingStaus = data["status"]
		#		"data" : {
		#		    "id" : "lckhw7k74ct",
		#		    "type" : "operation",
		#		    "operationType" : "deleteCertificate",
		#		    "createdBy" : "1888k3kizr3z",
		#		    "createdTime" : "2024-10-04T20:25:27Z",
		#		    "completedTime" : "2024-10-04T20:25:27Z",
		#		    "resourceId" : "3j5iupwihw0/serverCertificates/78b158361cd551c90e05f8d8b83f511e",
		#		    "resourceType" : "certificate",
		#		    "status" : "INPROGRESS",
		#		    "error" : null
		#		  }
    self.logger.log(reason + " call to Solace Cloud API succeeds. Operation id '" + id + "' is currently in '" + startingStaus + "' status.");
    self.waitForOperationToCompleteV2(service, id, startingStaus) 

  def installCertificate(self, service: str, cert: SolaceCloudInstalledCert, passPhrase: str):
    url = installCertUrl.replace("{serviceId}", service)
    url = url.replace("{certificateId}", cert.certificateId)
    payload = "{\"passphrase\": \"{passphrase}\"}";
    payload = payload.replace("{passphrase}", passPhrase);
    self.postAndWait("install cert", service, url, payload)
    
  def uploadCertificate(self, service: str, certPayload: str, privateKey: str):
    print("Uploading...") 
    url = uploadCertUrl.replace("{serviceId}", service)
    payload = "{\"certificate\": \"{cert}\",\"privateKey\": \"{key}\"}"
    payload = payload.replace("{cert}", certPayload)
    payload = payload.replace("{key}", privateKey)
    self.postAndWait("upload cert", service, url, payload)

  def getCustomCertificate(self, service: str) -> SolaceCloudInstalledCert:
    customCert = None
    listCerts = self.getAllCertificates(service)

    for cert in listCerts:
      if cert.certType == "CUSTOM":
        customCert = cert
        break
    return customCert
  
  def getAllCertificates(self, service: str) -> list:
    listCerts = list()
    url = getCertsUrl.replace("{serviceId}", service)
	  
    self.logger.log("Getting a list of all certs on service " + service)
    response = super().get("get certs", url)
    jsonResponse = json.loads(response.text)
		
    data = jsonResponse["data"]
    self.logger.log("There are " + str(len(data)) + " certs reported by the Solace Cloud API")
    for row in data:
      certificateId = row["id"]
      certificateType = row["certificateType"]
      scCert = self.getCertificate(service, certificateId)
      scCert.certType = certificateType
      listCerts.append(scCert)
    return listCerts
    
  def getCertificate(self, service: str, certificateId: str) -> SolaceCloudInstalledCert:
    url = getSingleCertUrl.replace("{serviceId}", service)
    url = url.replace("{certificateId}", certificateId)
    response = super().get("get cert", url)
    jsonResponse = json.loads(response.text)
		#	Eg:		{
		#			    "data": {
		#			        "installed": false,
		#			        "serialNumber": "0b:84:4e:b2:54:d7:03:a9:ab:60:71:38",
		#			        "id": "78b158361cd551c90e05f8d8b83f511e",
		#			        "validityNotBefore": "2024-09-18T16:18:56Z",
		#			        "type": "serverCertificate",
		#			        "validityNotAfter": "2025-09-18T16:23:56Z",
		#			        "subjectCN": "ssdp-dev-euw3-aza-edge-01.ee.iot.iov.dev.vhl-iov.private",
		#			        "certificateType": "CUSTOM",
		#			        "sha1Thumbprint": "360fe7207ead6e9dc356cb7706aab2c76fc07113"
		#			    }
		#			}
    data = jsonResponse["data"]
    subjectCN = data["subjectCN"]
    validityNotAfter = data["validityNotAfter"]
    installed = data["installed"]

    scCert =  SolaceCloudInstalledCert()
    scCert.serviceId = service
    scCert.certificateId = certificateId
    scCert.expiry = validityNotAfter
    scCert.cn = subjectCN
    scCert.installed = installed
		
    msg = "The cert on the '" + service + "' Solace Cloud service is: installed='" + str(installed) + "', cn=" + subjectCN + ", expiring on '" + validityNotAfter + "'."; 
    self.logger.log(msg);	    	
    return scCert
	
  def deleteCertificate(self, service: str, certificateId: str):
    url = deleteCertUrl.replace("{serviceId}", service)
    url = url.replace("{certificateId}", certificateId)
    response = super().delete("delete cert", url)
    jsonResponse = json.loads(response.text)
    data = jsonResponse["data"]

		#		"data" : {
		#		    "id" : "lckhw7k74ct",
		#		    "type" : "operation",
		#		    "operationType" : "deleteCertificate",
		#		    "createdBy" : "1888k3kizr3z",
		#		    "createdTime" : "2024-10-04T20:25:27Z",
		#		    "completedTime" : "2024-10-04T20:25:27Z",
		#		    "resourceId" : "3j5iupwihw0/serverCertificates/78b158361cd551c90e05f8d8b83f511e",
		#		    "resourceType" : "certificate",
		#		    "status" : "INPROGRESS",
		#		    "error" : null
		#		  }
    operationId = data["id"]
    status = data["status"]
    self.logger.log("Certificate delete call to Solace Cloud API succeeds. Operation id '" + operationId + "' is currently in '" + status + "' status.")
    self.waitForOperationToCompleteV2(service, operationId, status)

  def waitForOperationToCompleteV2(self, service: str, operationId: str, startingStaus: str) :
    status = startingStaus
    url = operationStatsUrl.replace("{serviceId}", service)
    url = url.replace("{operationId}", operationId)

    while status == "INPROGRESS":
      response = super().get("get operation status", url)
      jsonResponse = json.loads(response.text)
      data = jsonResponse["data"]

			#	Eg.		{
			#			    "data": {
			#			        "resourceId": "meii3hc038b/serverCertificates/4298ebc5b1a518d1e36c70cd2e366811",
			#			        "createdBy": "1888k3kizr3z",
			#			        "completedTime": "2024-10-04T20:56:33Z",
			#			        "createdTime": "2024-10-04T20:56:32Z",
			#			        "operationType": "uploadCertificate",
			#			        "id": "6beazkt4e2v",
			#			        "type": "operation",
			#			        "error": null,
			#			        "resourceType": "certificate",
			#			        "status": "SUCCEEDED"
	 
			#			}			
			#logger.info("Certificate upload call to Solace Cloud API succeeds. Operation id '" + operationId + "' is currently in '" + status + "' status.");
      operationIdRetreived = data["id"]
      status = data["status"]
      if not operationIdRetreived == operationId:
        raise RuntimeError("Unexpected condition. Solace cloud has retured a payload for operation id '" + operationIdRetreived + ", when '" + operationId + "' was expected.")

      time.sleep(3)

      if not (status == "SUCCEEDED" or status == "INPROGRESS"):
			  #validate(data); // throws the specific error if one has occurred else no action
        message = "Operation not completed as expected: " + status + ". "
        if "error" in data:
           error = data["error"]
           message = message + error["message"]
        raise RuntimeError(message)
			
			# important, this API V2 error pattern is not the same as the V0
			#failed EG:"data" : {
			#			    "id" : "e0siqizwfho",
			#			    "type" : "operation",
			#			    "operationType" : "uploadCertificate",
			#			    "createdBy" : "1888k3kizr3z",
			#			    "createdTime" : "2024-10-04T21:09:42Z",
			#			    "completedTime" : "2024-10-04T21:09:42Z",
			#			    "resourceId" : "meii3hc038b/serverCertificates/339a832bc72085e1ab4330b85d75fbcb",
			#			    "resourceType" : "certificate",
			#			    "status" : "FAILED",
			#			    "error" : {
			#			      "message" : "Failed to upload. Certificate already exists.",
			#			      "errorId" : "643f7a7a-9d24-4560-af20-232a67a33907"
			#			    }
			#			  }
    self.logger.log("Operation id '" + operationId + "' has sucesfully completed.")

