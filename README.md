# cfDns

Update CloudFlare DNS with a docker container.


## Compose File
```sh
version: "3.7"
########################### SERVICES
services:
  cfdns:
    image: ghcr.io/oomathurman/cfDns
    container_name: cfDns
    restart: unless-stopped
    environment:
      - domainName=
      - dnsRecords=root,*  # Use 'root' for '.domain.com'
      - apiEmail=
      - apiKey=
      - logLevel=WARNING
      - cronTime=*/5 * * * *
      - TZ=
```

## Environment
- domainName
	- example.com
- dnsRecords
	- do not use FQDN here, domainName is added in the script.
	- To update '.example.com' use 'root' as the record.  See example.
	- Comma separated. 
- apiEmail
	- your CloudFlare email
- apiKey
	- your CloudFlare api key
- logLevel
  - 'CRITICAL' - script crashing errors.
  - 'WARNING' - Warnings, records match.
  - 'INFO' - informational output
  - 'DEBUG'
- timer
	- cron timer [Crontab.guru](https://crontab.guru/#*/5_*_*_*_*)
- TZ
  - Set timezone for accurate logs
