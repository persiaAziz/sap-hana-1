import requests
from bs4 import BeautifulSoup
import urllib
import argparse

def authenticate_SMP(s_user,s_password):

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

    requestBody = "tenantId={0}&idpName={1}&requestUrl={2}&requestId={3}&relayState={4}&action=sso&signature={5}"            .format(urllib.parse.quote(tenantId),urllib.parse.quote(idpName),
            urllib.parse.quote(requestUrl),urllib.parse.quote(requestId),
            urllib.parse.quote(relayState),urllib.parse.quote(signature))

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


    soup = BeautifulSoup(re3.content, 'html.parser')
    for input_h in soup.find_all('input'):
        print(input_h.get('name'))
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

    requestBody="utf8=%E2%9C%93&authenticity_token={0}&xsrfProtection={1}&method=POST&idpSSOEndpoint={2}\
&SAMLRequest={3}&RelayState={4}&&targetUrl=&sourceUrl=&org=&spId={5}&spName={6}\
&mobileSSOToken=&tfaToken=&css=&j_username={7}&j_password={8}".format(urllib.parse.quote(auth_token),
        urllib.parse.quote(xsrfProtection),
        urllib.parse.quote(idp_sso_endpoint), urllib.parse.quote(saml_request),
        urllib.parse.quote(relayState),urllib.parse.quote(data_spid),
        urllib.parse.quote(data_spname),urllib.parse.quote(s_user),
        urllib.parse.quote(s_password))
    print(requestBody)

def main():
    parser = argparse.ArgumentParser(description='Process ')
    parser.add_argument('-u', "--s_user", required=True, help='S_user')
    parser.add_argument('-p', "--s_password", required=True, help='S_password')
    args = parser.parse_args()
    authenticate_SMP(args.s_user,args.s_password)

if __name__=="__main__":
    main()
