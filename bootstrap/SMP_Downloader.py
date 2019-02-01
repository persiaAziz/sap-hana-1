'''
This script searches the SAP service market place by product Id and downloads the files

Input: 
    1. SAP user ID
    2. SAP user password
    3. Package ID to search for
'''

import requests
from bs4 import BeautifulSoup
import urllib
import argparse
from http import cookies
import json

'''
Function: authenticate_SMP
Description: Authenticates to the Service Market place using the user's SAP account crendentials.
             The authenticaion method is a SAML based Single Sign On
Parameters: s_user - SAP user name
            s_password - SAP password
Returns: requests.session() -  Authenticated session to launchpad.support.sap.com
'''

def authenticate_SMP(s_user,s_password):

    print("\nAuthenticating to the SAP Service Market Place with the provided crendentials")
    ### step 1: get the idpname, tenantid etc.
    s_launch = requests.session()
    re1 = s_launch.get("https://launchpad.support.sap.com", headers={"Connection":"Kepp-Alive"})
    assert (200==re1.status_code),"Authentication failed."
    soup = BeautifulSoup(re1.content, 'html.parser')
    for input_h in soup.find_all('input'):
        #print(input_h.get('name'))
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

    cookie_launch = re1.cookies

    requestBody = "tenantId={0}&idpName={1}&requestUrl={2}&requestId={3}&relayState={4}&action=sso&signature={5}".format(urllib.parse.quote(tenantId),
            urllib.parse.quote(idpName),
            urllib.parse.quote(requestUrl),urllib.parse.quote(requestId),
            urllib.parse.quote(relayState),urllib.parse.quote(signature))

    ### step 2: post to idp with the information
    s_auth = requests.session()
    re2 = s_auth.post("https://authn.hana.ondemand.com/saml2/sp/mds",
            headers={"Referer":"https://launchpad.support.sap.com/", "Content-Type":"application/x-www-form-urlencoded"},data=requestBody)
    assert (200==re2.status_code),"Authentication failed."

    #get the saml request
    soup = BeautifulSoup(re2.content, 'html.parser')
    for input_h in soup.find_all('input'):
        if "SAMLRequest" == input_h.get('name'):
            saml_request = input_h.get('value')
        if "RelayState" == input_h.get('name'):
            relayState_auth = input_h.get('value')
    requestBody = "SAMLRequest={0}&RelayState={1}".format(urllib.parse.quote(saml_request),urllib.parse.quote(relayState))

    ### step 3: pass the saml request
    s_accounts = requests.session()
    re3=s_accounts.post("https://accounts.sap.com/saml2/idp/sso/accounts.sap.com",
            headers={"Referer":"https://authn.hana.ondemand.com/saml2/sp/mds",
                    "Content-Type":"application/x-www-form-urlencoded",
                    "Content-Length": str(len(requestBody))},
            data=requestBody)
    assert (200==re3.status_code),"Authentication failed."

    # Retrieve the authenticity token, cross-site request forgery  protection, IDP endpoint, service provider id and name
    soup = BeautifulSoup(re3.content, 'html.parser')
    for input_h in soup.find_all('input'):
        if "authenticity_token" == input_h.get('name'):
            auth_token = input_h.get('value')
        if "xsrfProtection" == input_h.get('name'):
            xsrfProtection = input_h.get('value')
        if "idpSSOEndpoint" == input_h.get('name'):
            idp_sso_endpoint = input_h.get('value')
        if "spId" == input_h.get('name'):
            data_spid = input_h.get('value')
        if "spName" == input_h.get('name'):
            data_spname = input_h.get('value')

    requestBody2="utf8=%E2%9C%93&"+urllib.parse.urlencode({"authenticity_token":auth_token,"xsrfProtection":xsrfProtection,"method":"POST",
        "idpSSOEndpoint":idp_sso_endpoint,"SAMLRequest":saml_request,"RelayState":relayState_auth,"targetUrl":"",
        "sourceUrl":"","org":"","spId":data_spid,"spName":data_spname,"mobileSSOToken":"",
        "tfaToken":"","css":"","j_username":s_user,"j_password":s_password})

    #Step 4: Send the credentials and get the appropriate cookies
    re4 = s_accounts.post("https://accounts.sap.com/saml2/idp/sso/accounts.sap.com", 
            headers={"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Referer":"https://accounts.sap.com/saml2/idp/sso/accounts.sap.com",
                    "Upgrade-Insecure-Requests": "1", 
                    "DNT":"1", 
                    "Content-Type": "application/x-www-form-urlencoded", 
                    "Accept-Encoding": "gzip, deflate, br",
                    "Content-Length":str(len(requestBody2))},
            data=requestBody2)
    assert (200==re4.status_code),"Authentication failed."

    soup = BeautifulSoup(re4.content, 'html.parser')
    for input_h in soup.find_all('input'):
        if "SAMLResponse" == input_h.get('name'):
            saml_response = input_h.get('value')

    cookie_processor = cookies.SimpleCookie()
    cookie_processor.load(re4.cookies)
    cookie_launch.set('IDP_SESSION_MARKER_accounts',cookie_processor['IDP_SESSION_MARKER_accounts'].value, domain= ".sap.com",path="/")

    #Step 5: Pass the SAML response to the idp
    requestBody5 = "utf8=%E2%9C%93&"+urllib.parse.urlencode({"authenticity_token":auth_token,"SAMLResponse":saml_response,"RelayState":relayState_auth})
    re5 = s_auth.post("https://authn.hana.ondemand.com/saml2/sp/acs/supportportal/supportportal",
            headers={"Referer":"https://accounts.sap.com/saml2/idp/sso/accounts.sap.com",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Upgrade-Insecure-Requests": "1", "DNT":"1",
                    "Content-Length":str(len(requestBody5))},
            data=requestBody5)
    assert (200==re5.status_code),"Authentication failed."

    #step 6:
    requestBody6 = "utf8=%C3%A2%C2%9C%C2%93&"+urllib.parse.urlencode({"authenticity_token":auth_token,"SAMLResponse":saml_response,"RelayState":relayState_auth})
    re6 = s_launch.post("https://launchpad.support.sap.com/",allow_redirects=False,
          headers={"Referer":"https://authn.hana.ondemand.com/saml2/sp/acs/supportportal/supportportal",
              "Content-Type":"application/x-www-form-urlencoded", "Upgrade-Insecure-Requests":"1",
              "Accept-Encoding": "gzip, deflate, br","Accept":"text/html, application/xhtml+xml, application/xml; q=0.9, */*; q=0.8","Connection":"Keep-Alive",
              "Content-Length":str(len(requestBody6))}, cookies=cookie_launch,data=requestBody6)

    #the s_launch session already has the cookie it needs.
    re7 = s_launch.get("https://launchpad.support.sap.com", 
          headers={"Referer":"https://authn.hana.ondemand.com/saml2/sp/acs/supportportal/supportportal"})
    print("Authentication succeeded")
    return s_launch

'''
Function: download_SMP
Description: Downloads the packages corresponding to the provided package ID
Parameters: session_launch - Authenticated session to launchpad.support.sap.com
            packageId - PackageID
            s_user - SAP account user ID
            s_password - SAP account password
Returns: None
'''

def download_SMP(session_launch, packageId,s_user,s_password):

    re8 = session_launch.get("https://launchpad.support.sap.com/services/odata/svt/swdcuisrv/SearchResultSet?SEARCH_MAX_RESULT=500&RESULT_PER_PAGE=500&SEARCH_STRING={0}".format(packageId),
          headers={"Accept":"application/json"})
    downloadlinks_json = json.loads(re8.content)
    for i in downloadlinks_json['d']['results']:
        print("Found {0}. \n Downloading.....".format(i['Title']))
        re = requests.get(i['DownloadDirectLink'], auth=(s_user,s_password), allow_redirects=False)
        re2 = requests.get(re.headers['Location'], auth=(s_user,s_password), stream=True)
        savefile = i['Title']
        with open(savefile,'wb') as f:
            for chunk in re2.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print("Downloaded to file: {0}".format(savefile))



def main():
    parser = argparse.ArgumentParser(description='Process ')
    parser.add_argument('-u', "--s_user", required=True, help='S_user')
    parser.add_argument('-p', "--s_password", required=True, help='S_password')
    parser.add_argument('-i', "--package_id", required=True, help='Package Id of the package to download')
    args = parser.parse_args()
    try:
       session_launchpad = authenticate_SMP(args.s_user,args.s_password)
    except:
       print("Authentication failed. You need valid SAP credentials")
       exit(1)

    try:
       download_SMP(session_launchpad,args.package_id,args.s_user,args.s_password)
    except:
       print("Download of the package:{0} failed".format(args.package_id))

if __name__=="__main__":
    main()
