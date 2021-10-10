Simple load test script for http://miloszhoc.cloud website created using locust.

To run this script use `docker-compose up -d --scale worker=4` command.    

Locust web UI is available via 8089 port.     

Test requires .env file with the following environmental variables:
* username
* password
