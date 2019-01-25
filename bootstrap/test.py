import requests
from bs4 import BeautifulSoup
import urllib

### step 1: get the idpname, tenantid etc.
s = requests.session()
re1 = s.get("https://launchpad.support.sap.com")
soup = BeautifulSoup(re1.content, 'html.parser')
for input_h in soup.find_all('input'):
    print(input_h.get('name'))
    if "requestId" == input_h.get('name'):
        requestId = input_h.get('value')
    if "tenantId" == input_h.get('name'):
        tenantId = input_h.get('value')
    if "requestUrl" == input_h.get('name'):
        requestUrl = input_h.get('value')
    if "idpName" == input_h.get('name'):
        idpName = input_h.get('value')
    if "signature" == input_h.get('name'):
        signature = input_h.get('value')
    if "relayState" == input_h.get('name'):
        relayState = input_h.get('value')
    
requestBody = "tenantId={0}&idpName={1}&requestUrl={2}&requestId={3}&relayState={4}&action=sso&signature={5}".format(urllib.parse.quote(tenantId),urllib.parse.quote(idpName),urllib.parse.quote(requestUrl),urllib.parse.quote(requestId),urllib.parse.quote(relayState),urllib.parse.quote(signature))

### step 2: post to idp with the information
re2=requests.post("https://authn.hana.ondemand.com/saml2/sp/mds",headers={"Referer":"https://launchpad.support.sap.com/", "Content-Type":"application/x-www-form-urlencoded"},data=requestBody)

#get the saml request
soup = BeautifulSoup(re2.content, 'html.parser')
for input_h in soup.find_all('input'):
    if "SAMLRequest" == input_h.get('name'):
        saml_request = input_h.get('value')
print("saml=>",saml_request)
requestBody = "SAMLRequest={0}&RelayState={1}".format(urllib.parse.quote(saml_request),urllib.parse.quote(relayState))
### step 3: pass the saml request
re3=requests.post("https://accounts.sap.com/saml2/idp/sso/accounts.sap.com",headers={"Referer":"https://authn.hana.ondemand.com/saml2/sp/mds", "Content-Type":"application/x-www-form-urlencoded", "Content-Length": str(len(requestBody))},data=requestBody)


soup = BeautifulSoup(re2.content, 'html.parser')
for input_h in soup.find_all('input'):
    if "authenticity_token" == input_h.get('name'):
        auth_token = input_h.get('value')
    if "xsrfProtection" == input_h.get('name'):
        xsrfProtection = input_h.get('value')
    if "idpSSOEndpoint" == input_h.get('name'):
        idp_sso_endpoint = input_h.get('value')
    if "data-spid" == input_h.get('name'):
        data-spid = input_h.get('value')
    if "data-spname" == input_h.get('name'):
        data-spname = input_h.get('value')

requestBody="utf8=%E2%9C%93&authenticity_token={0}&xsrfProtection={1}&"
print(re3.status_code)
