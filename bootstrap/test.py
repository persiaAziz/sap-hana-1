import requests
from bs4 import BeautifulSoup
import urllib
import argparse
import pdb 

def authenticate_SMP(s_user,s_password):

    ### step 1: get the idpname, tenantid etc.
    s = requests.session()
    re1 = s.get("https://launchpad.support.sap.com")
    print("1: ", re1.status_code)
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

    requestBody = "tenantId={0}&idpName={1}&requestUrl={2}&requestId={3}&relayState={4}&action=sso&signature={5}".format(urllib.parse.quote(tenantId),
            urllib.parse.quote(idpName),
            urllib.parse.quote(requestUrl),urllib.parse.quote(requestId),
            urllib.parse.quote(relayState),urllib.parse.quote(signature))

    ### step 2: post to idp with the information
    re2=requests.post("https://authn.hana.ondemand.com/saml2/sp/mds",headers={"Referer":"https://launchpad.support.sap.com/", "Content-Type":"application/x-www-form-urlencoded"},data=requestBody)
    print("2: ",re2.status_code)
    #save the cookie
    cookie = re2.headers['set-cookie']
    #get the saml request
    soup = BeautifulSoup(re2.content, 'html.parser')
    for input_h in soup.find_all('input'):
        if "SAMLRequest" == input_h.get('name'):
            saml_request = input_h.get('value')
    #print("saml=>",saml_request)
    requestBody = "SAMLRequest={0}&RelayState={1}".format(urllib.parse.quote(saml_request),urllib.parse.quote(relayState))

    ### step 3: pass the saml request
    s_accounts = requests.session()
    re3=s_accounts.post("https://accounts.sap.com/saml2/idp/sso/accounts.sap.com",headers={"Referer":"https://authn.hana.ondemand.com/saml2/sp/mds", "Content-Type":"application/x-www-form-urlencoded", "Content-Length": str(len(requestBody))},data=requestBody)
    print("3: ",re3.status_code)
    a_cookies = re3.headers['Set-Cookie']
    soup = BeautifulSoup(re3.content, 'html.parser')
    for input_h in soup.find_all('input'):
        #print(input_h.get('name'))
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

    #pdb.set_trace()
    requestBody2="utf8=%E2%9C%93&"+urllib.parse.urlencode({"authenticity_token":auth_token,"xsrfProtection":xsrfProtection,"method":"POST",
        "idpSSOEndpoint":idp_sso_endpoint,"SAMLRequest":saml_request,"RelayState":relayState,"targetUrl":"",
        "sourceUrl":"","org":"","spId":data_spid,"spName":data_spname,"mobileSSOToken":"",
        "tfaToken":"","css":"","j_username":s_user,"j_password":s_password})

    #Step 4: Send the credentials and get the appropriate cookies
    print(requestBody2)
    cookie = a_cookies
    re4 = s_accounts.post("https://accounts.sap.com/saml2/idp/sso/accounts.sap.com", headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Referer":"https://accounts.sap.com/saml2/idp/sso/accounts.sap.com","Upgrade-Insecure-Requests": "1", "DNT":"1", "Content-Type": "application/x-www-form-urlencoded", "Cookie": cookie, "Accept-Encoding": "gzip, deflate, br","Content-Length":str(len(requestBody2))}, data=requestBody2)
    print(re4.headers)
    print("4: ",re4.status_code)

    #Step 5: 

def main():
    parser = argparse.ArgumentParser(description='Process ')
    parser.add_argument('-u', "--s_user", required=True, help='S_user')
    parser.add_argument('-p', "--s_password", required=True, help='S_password')
    args = parser.parse_args()
    authenticate_SMP(args.s_user,args.s_password)

if __name__=="__main__":
    main()
