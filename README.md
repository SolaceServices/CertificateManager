# CertificateManager
Python scripts for managing Broker server certificates

## Introduction
At this time, there is no user interface provided by SOlace to upload custom server ceritifcates to Solace brokers. We can upload Certificate Domain Authorities (CAs), but not the certificates. This set of scripts fills the gap and allows reporting, installation and deletion of certificates.

These toools use the Solace Cloud API (V2). This tool uploads certicates and makes cert related requests to the Solace Home Cloud, which in turn communicates with the broker. 

**IMPORTANT:** This code is NOT officially support Solace product. This tool was created by Mike O'Brien in the Solace Services team to augment Solace product, and is provided as an example. Do not contact the Solace support team to report any issues with this tool. 

## Requirements
You need to have:
1) A certificate file, in PEM format, with intermediate CAs inline as part of the file. The following is an example of the file format, with most of the content removed for brevity:

> -----BEGIN CERTIFICATE-----
THISISJUNKMIKEPUTHERE+uMA0GCSqGSIb3DQEBCwUAMIGdMQswCQYDVQQGEwJG
UjEOMAwGA1UEBxMFUGFyaXMxHDAaBgNVBAoTE1BTQSBQZXVnZW90IENpdHJvZW4xFzAVBgNVBAsT
DjAwMDIgMzE5MTg3MzA4MSAwHgYDVQQLExdDZXJ0aWZpY2FPjRA0wzj5b8mgr74BQzyf5YVUu1sH
dNDRLxz1K0aYEaGvL/GngFf6cKdKb20Nofyee+8vEoAY
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
THISISJUNKMIKEPUTHEREKeC/qxi5m5wrdCzyjANBgkqhkiG9w0BAQsFADCBmzEL
MAkGA1UEBhMCRlIxDjAMBgNVBAcTBVBhcmlzMRwwGgYDVQQKExNQU0EgUGV1Z2Vv
YqRKpyO+KpJ2545hec8Sg0SQ91uYqxgmFwN6ZNrMa8Dsjx+i4wN/zzPsADeuGO4a
TJ888os=
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
THISISJUNKMIKEPUTHERExsa/qyZMGnJbr997zANBgkqhkiG9w0BAQsFADCBmzEL
MAkGA1UEBhMCRlIxDjAMBgNVBAcTBVBhcmlzMRwwGgYDVQQKExNQU0EgUGV1Z2Vv
ja10NwnUYG2gBMDodX7sZWU9oNZ1CyPsDRxZIyHTgF8K6V71qldHuu7BAQSb4OUu
fyx5q0y/
-----END CERTIFICATE-----
2) A Private key file
3) A passphrase for the key
4) Know the service ID of the Solace Cloud broker
5) Have a token with permissions to acton the broker service. Put the token in a text file somewhere on your local drive. You will supply this file to each of the scripts.

## Running the scripts

### Report
This tool lists out all certificates that are uploaded onto the broker.
> python CertReport.py --service=juw0xswqqqee3 --token=../token.txt

**output:**
Runing CertificateTool version 1.00
Acting on Solace Cloud Service juw0xswqqqee3
Token file found and loaded.
Fetching all certs for the broker with service id 'juw0xswqqqee3' through the Solace Home Cloud API...
1 certificates found on service juw0xswqqqee3

Certificate #1: - - - - -   
type:CUSTOM  
cn:my.fqdn.at.my.domain  
expiry:2025-10-25T18:08:07Z  
installed:True  

## Upload and Install
This tool uploads your custom cert to the broker and installs it.
> python CertInstall.py --service=juw0xswqqqee3 --token=../token.txt --cert=../testCert.pem --key=../testKey.key --passPhrase=yxtr34fv

**output:**
Runing CertificateTool version 1.00  
Acting on Solace Cloud Service juw0xswqqqee3  
Token file found and loaded.  
Uploading your certificate ../testCert.pem to the broker with service ID 'juw0xswqqqee3' through the Solace Home Cloud (SaS) API...  
Uploading...  
Cert was uploaded sucesfully. Installing...  
Cert wasinstalled sucesfully. Fetching it to double check...  
- - - -  
Cert uploaded and installed:  
type:CUSTOM  
cn:my.fqdn.at.my.domain  
expiry:2025-10-25T18:08:07Z  
installed:True  
Tool completed sucessfully.  

## Delete
Solace Cloud will typically only put one certificate on a broker. However, it is possible that you could have extra certificates that have been uploaded, but not installed. In this case, youcan use this delete script to remove a custom cert from a broker. 

> python CertDelete.py --service=juw0xswqqqee3 --token=../token.txt

**output:**
Runing CertificateTool version 1.00  
Acting on Solace Cloud Service juw0xswqqqee3  
Token file found and loaded.  
Deleting any uninstalled custom certificates for the broker with service id 'juw0xswqqqee3' through the Solace Home Cloud API...  
1 certificates were deleted on service juw0xswqqqee3  

## Feedback?
Send feature requests, defects and comments to (mailto:mike.obrien@solace.com)
