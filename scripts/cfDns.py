import requests, os, re, json, logging, sys
sys.tracebacklimit = 0

### From Compose File
domainName = os.environ['domainName']
dnsRecords = os.environ['dnsRecords']
apiEmail = os.environ['apiEmail']
apiKey = os.environ['apiKey']
logLevel = os.environ['logLevel']

### Loggin Settings
logging.basicConfig(format='[%(levelname)s] %(asctime)s : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logLevel.upper())
logger = logging.getLogger(__name__)

# Make dnsRecords a list, if multiple provided
try:
    dnsRecords = dnsRecords.split(',')
    print(dnsRecords.split(','))
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
    sites=['https://ICanHazIP.com', 'https://CloudFlare.com/cdn-cgi/trace']
    for site in sites:
        try:
            retVar
            continue
        except:
            try:
                response, code, header = restCall("GET", site, headers={})
                if 'icanhazip' in site.lower():
                    retVar =  response.text.strip()
                if 'cloudflare' in site.lower():
                    retVar =  re.search(r"ip=(.*)", response.text).group(1)
            except:
                logger.warning(f'{site} failed')
    try:
        return retVar
    except:
        logger.critical(f'No sites available. Verify Internet and DNS Resolution')
        quit()

def getZoneId():
    # Find Zone Record ID
    try:
        response, code, header = restCall("GET", cfURL, headers=authHeaders)
        if code != 200:
            quit()
        for zone in response.json()['result']:
            if zone['name'].lower() == domainName.lower():
                return zone['id']
    except:
        logger.critical(f'Value Error see below:')
        raise ValueError(f'\n  Something went wrong. \
            \n  Please verify your apiEmail, and apiKey \
            \n  apiEmail : {apiEmail} \
            \n  apiKey   : {apiKey}')

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
    try:
        return retVar, recordIp
    except:
        logger.critical(f'Verify Records. Not all are matching.')
        quit()
    

def patchRecord(wanIP, zoneId, recordId):
    # Patch DNS Record
    response, code, header = restCall("PATCH", f'{cfURL}/{zoneId}/dns_records/{recordId}', headers=authHeaders, body=json.dumps({"content": wanIP}))
    return response.json()["success"], response.json()['errors'], response.json()['messages']

def main():
    logger.debug('Checking WAN IP')
    # Basic error checking. sort it out.
    for var in ['domainName', 'dnsRecords', 'apiEmail', 'apiKey', 'logLevel']:
        if var not in globals():
            logger.critical(f'Value Error')
            raise ValueError(f'\n  Looks like a variable ({var}) is missing. \
                \n  Please verify env settings. \
                \n  Closing until fixed.')
    # Do you have a wan IP?
    wanIP = getCurrentIP()
    logger.debug(f'Wan IP {wanIP}')
    # Does CloudFlare let you in?
    zoneId = getZoneId()
    logger.debug(f'Domain Zone Id {zoneId}')
    # You probly want to find the correct record now
    for recordName in dnsRecords:
        if recordName.lower() == 'root':
            recordName = ''
        recordId, recordIp = getRecordId(recordName, zoneId)
        if recordIp == wanIP:
            logger.debug(f'Record ({recordName}) already has value: {recordIp}')
            continue
        logger.info(f'Updating ({recordName}).{domainName.lower()} to {wanIP}')
        # Update recordId
        success, error, message = patchRecord(wanIP, zoneId, recordId)
        if success:
            logger.info(f'Successfully updated ({recordName})')
        else:
            logger.error(f'{error} : {message}')

if __name__ == "__main__":
    main()