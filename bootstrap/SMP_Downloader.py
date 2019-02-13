'''
This script searches the SAP service market place by product Id and downloads the files

Input: 
    1. SAP user ID
    2. SAP user password
    3. List of package IDs to search for
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

    URL_sap_launchpad = "https://launchpad.support.sap.com"
    URL_sap_auth = "https://authn.hana.ondemand.com/saml2/sp/mds"
    URL_sap_accounts = "https://accounts.sap.com/saml2/idp/sso/accounts.sap.com"
    URL_sap_auth_portal = "https://authn.hana.ondemand.com/saml2/sp/acs/supportportal/supportportal"

    print("\nAuthenticating to the SAP Service Market Place with the provided crendentials")
    ### step 1: get the idpname, tenantid etc.
    s_launch = requests.session()
    response1 = s_launch.get(URL_sap_launchpad, headers={"Connection":"Keep-Alive"})
    assert (200==response1.status_code),"Authentication failed."
    soup = BeautifulSoup(response1.content, 'html.parser')
    for input_h in soup.find_all('input'):
        input_field = input_h.get('name')
        input_value = input_h.get('value')
        if "requestId" == input_field:
            requestId = input_value
        elif "tenantId" == input_field:
            tenantId = input_value
        elif "requestUrl" == input_field:
            requestUrl = input_value
        elif "idpName" == input_field:
            idpName = input_value
        elif "signature" == input_field:
            signature = input_value
        elif "relayState" == input_field:
            relayState = input_value

    cookie_launch = response1.cookies

    requestBody = "tenantId={0}&idpName={1}&requestUrl={2}&requestId={3}&relayState={4}&action=sso&signature={5}".format(urllib.parse.quote(tenantId),
            urllib.parse.quote(idpName),
            urllib.parse.quote(requestUrl),urllib.parse.quote(requestId),
            urllib.parse.quote(relayState),urllib.parse.quote(signature))

    ### step 2: post to idp with the information
    s_auth = requests.session()
    response2 = s_auth.post(URL_sap_auth,
            headers={"Referer":URL_sap_launchpad, "Content-Type":"application/x-www-form-urlencoded"},data=requestBody)
    assert (200==response2.status_code),"Authentication failed."

    #get the saml request
    soup = BeautifulSoup(response2.content, 'html.parser')
    for input_h in soup.find_all('input'):
        if "SAMLRequest" == input_h.get('name'):
            saml_request = input_h.get('value')
        if "RelayState" == input_h.get('name'):
            relayState_auth = input_h.get('value')
    requestBody = "SAMLRequest={0}&RelayState={1}".format(urllib.parse.quote(saml_request),urllib.parse.quote(relayState))

    ### step 3: pass the saml request
    s_accounts = requests.session()
    response3=s_accounts.post(URL_sap_accounts,
            headers={"Referer":URL_sap_auth,
                    "Content-Type":"application/x-www-form-urlencoded",
                    "Content-Length": str(len(requestBody))},
            data=requestBody)
    assert (200==response3.status_code),"Authentication failed."

    # Retrieve the authenticity token, cross-site request forgery  protection, IDP endpoint, service provider id and name
    soup = BeautifulSoup(response3.content, 'html.parser')
    for input_h in soup.find_all('input'):
        input_field = input_h.get('name')
        input_value = input_h.get('value')
        if "authenticity_token" == input_field:
            auth_token = input_value
        elif "xsrfProtection" == input_field:
            xsrfProtection = input_value
        elif "idpSSOEndpoint" == input_field:
            idp_sso_endpoint = input_value
        elif "spId" == input_field:
            data_spid = input_value
        elif "spName" == input_field:
            data_spname = input_value

    requestBody2="utf8=%E2%9C%93&"+urllib.parse.urlencode({"authenticity_token":auth_token,"xsrfProtection":xsrfProtection,"method":"POST",
        "idpSSOEndpoint":idp_sso_endpoint,"SAMLRequest":saml_request,"RelayState":relayState_auth,"targetUrl":"",
        "sourceUrl":"","org":"","spId":data_spid,"spName":data_spname,"mobileSSOToken":"",
        "tfaToken":"","css":"","j_username":s_user,"j_password":s_password})

    #Step 4: Send the credentials and get the appropriate cookies
    response4 = s_accounts.post(URL_sap_accounts,
            headers={"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Referer":URL_sap_accounts,
                    "Upgrade-Insecure-Requests": "1", 
                    "DNT":"1", 
                    "Content-Type": "application/x-www-form-urlencoded", 
                    "Accept-Encoding": "gzip, deflate, br",
                    "Content-Length":str(len(requestBody2))},
            data=requestBody2)
    assert (200==response4.status_code),"Authentication failed."

    soup = BeautifulSoup(response4.content, 'html.parser')
    for input_h in soup.find_all('input'):
        if "SAMLResponse" == input_h.get('name'):
            saml_response = input_h.get('value')

    cookie_processor = cookies.SimpleCookie()
    cookie_processor.load(response4.cookies)
    cookie_launch.set('IDP_SESSION_MARKER_accounts',cookie_processor['IDP_SESSION_MARKER_accounts'].value, domain= ".sap.com",path="/")

    #Step 5: Pass the SAML response to the idp
    requestBody5 = "utf8=%E2%9C%93&"+urllib.parse.urlencode({"authenticity_token":auth_token,"SAMLResponse":saml_response,"RelayState":relayState_auth})
    response5 = s_auth.post(URL_sap_auth_portal,
            headers={"Referer":URL_sap_accounts,
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Upgrade-Insecure-Requests": "1", "DNT":"1",
                    "Content-Length":str(len(requestBody5))},
            data=requestBody5)
    assert (200==response5.status_code),"Authentication failed."

    #step 6: use the authenticity token to get the session cookie
    requestBody6 = "utf8=%C3%A2%C2%9C%C2%93&"+urllib.parse.urlencode({"authenticity_token":auth_token,"SAMLResponse":saml_response,"RelayState":relayState_auth})
    response6 = s_launch.post(URL_sap_launchpad,allow_redirects=False,
          headers={"Referer":URL_sap_auth_portal,
                   "Content-Type":"application/x-www-form-urlencoded",
                   "Upgrade-Insecure-Requests":"1",
                   "Accept-Encoding": "gzip, deflate, br",
                   "Accept":"text/html, application/xhtml+xml, application/xml; q=0.9, */*; q=0.8",
                   "Connection":"Keep-Alive",
                   "Content-Length":str(len(requestBody6))},
          cookies=cookie_launch,data=requestBody6)

    #step 7: store the session cookie in s_launch.
    response7 = s_launch.get(URL_sap_launchpad,
          headers={"Referer":URL_sap_auth_portal})
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

    resp_laundhpad = session_launch.get("https://launchpad.support.sap.com/services/odata/svt/swdcuisrv/SearchResultSet?SEARCH_MAX_RESULT=500&RESULT_PER_PAGE=500&SEARCH_STRING={0}".format(packageId),
          headers={"Accept":"application/json"})
    downloadlinks_json = json.loads(resp_laundhpad.content)
    for i in downloadlinks_json['d']['results']:
        print("Found {0}. \n Downloading.....".format(i['Title']))
        resp_download = requests.get(i['DownloadDirectLink'], auth=(s_user,s_password), allow_redirects=False)
        response = requests.get(resp_download.headers['Location'], auth=(s_user,s_password), stream=True)
        savefile = i['Title']
        with open(savefile,'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print("Downloaded to file: {0}".format(savefile))



def main():
    parser = argparse.ArgumentParser(description='Process ')
    parser.add_argument('-u', "--s_user", required=True, help='S_user')
    parser.add_argument('-p', "--s_password", required=True, help='S_password')
    parser.add_argument('-i', "--package_id", required=True, type=str, nargs='+', help='Package Ids of the package to download')
    args = parser.parse_args()
    try:
       session_launchpad = authenticate_SMP(args.s_user,args.s_password)
    except:
       print("Authentication failed. You need valid SAP credentials")
       exit(1)

    try:
       for package_i in args.package_id:
           download_SMP(session_launchpad,package_i,args.s_user,args.s_password)
    except Exception as e:
        print("Download of the package:{0} failed: {1}".format(args.package_id, str(e)))

if __name__=="__main__":
    main()
