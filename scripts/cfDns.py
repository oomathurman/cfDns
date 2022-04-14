import requests, os, re, json
from colorama import Fore, Style

domainName = os.environ['domainName']
dnsRecords = os.environ['dnsRecords']
apiEmail = os.environ['apiEmail']
apiKey = os.environ['apiKey']

try:
    dnsRecords.split(',')
except:
    pass

cfURL = "https://api.cloudflare.com/client/v4/zones"
authHeaders = {
    "X-Auth-Email": apiEmail,
    "X-Auth-Key": apiKey
}

def restCall(method, url, headers, body='{}'):
    response = requests.request(method, url, headers=headers, data=body)
    response_code = response.status_code
    response_header = response.headers
    return response, response_code, response_header


def getCurrentIP():
    # Get your WAN IP
    try:
        URL = 'https://ICanHazIP.com1'
        response, code, header = restCall("GET", URL, headers={})
        retVar =  response.text.strip()
    except:
        URL = 'https://CloudFlare.com/cdn-cgi/trace'
        response, code, header = restCall("GET", URL, headers={})
        retVar =  re.search(r"ip=(.*)", response.text).group(1)
    return retVar

def getZoneId():
    # Find Zone Record ID
    try:
        response, code, header = restCall("GET", cfURL, headers=authHeaders)
        for zone in response.json()['result']:
            if zone['name'].lower() == domainName.lower():
                return zone['id']
    except:
        raise ValueError(Fore.RED + f'\n  Something went wrong. \
            \n  Please verify your apiEmail, and apiKey \
            \n  apiEmail : {apiEmail} \
            \n  apiKey   : {apiKey}' + Style.RESET_ALL)

def getRecordId(recordName, zoneId):
    # Finding the records to update
    response, code, header = restCall("GET", f'{cfURL}/{zoneId}/dns_records', headers=authHeaders)
    for record in response.json()['result']:
        if recordName.lower() == "":
            if record['name'] == f'{domainName.lower()}':
                retVar = record['id']
                recordIp = record['content']
        else:
            if record['name'] == f'{recordName.lower()}.{domainName.lower()}':
                retVar = record['id']
                recordIp = record['content']
    return retVar, recordIp

def patchRecord(wanIP, zoneId, recordId):
    # Patch DNS Record
    response, code, header = restCall("PATCH", f'{cfURL}/{zoneId}/dns_records/{recordId}', headers=authHeaders, body=json.dumps({"content": wanIP}))
    return response.json()["success"], response.json()['errors'], response.json()['messages']



def main():
    # Basic error checking. sort it out.
    for var in ['domainName', 'dnsRecords', 'apiEmail', 'apiKey']:
        if var not in globals():
            raise ValueError(Fore.RED + f'\n  Looks like a variable ({var}) is missing. \
                \n  Please verify env settings. \
                \n  Closing until fixed.' + Style.RESET_ALL)
    # Do you have a wan IP?
    wanIP = getCurrentIP()
    print(f'Wan IP : {wanIP}')
    # Does CloudFlare let you in?
    zoneId = getZoneId()
    print(f'Domain Zone Id : {zoneId}')
    # You probly want to find the correct record now
    for recordName in dnsRecords:
        if recordName.lower() == 'root':
            recordName = ''
        recordId, recordIp = getRecordId(recordName, zoneId)
        if recordIp == wanIP:
            print(f'Record already set : {recordName} @ {recordIp} == {wanIP}')
            continue
        print(f'Record to update : {recordName}.{domainName.lower()} \
            \n  ID : {recordId}')
        # Update recordId
        success, error, message = patchRecord(wanIP, zoneId, recordId)
        if success:
            print('  UPDATED!')
        else:
            print(f'Errors: {error}')
            print(f'Message: {message}')


if __name__ == "__main__":
    main()