#!/bin/sh -e

echo installing jq
sudo apt install jq -y

echo Adding Cassandra package to repository
curl -X POST --header 'Content-Type: application/vnd.dcos.package.repository.add-request+json;charset=utf-8;version=v1' --header 'Accept: application/vnd.dcos.package.repository.add-response+json;charset=utf-8;version=v1' -d '  {"name": "cassandra", "uri": "https://px-dcos.s3.amazonaws.com/v2/cassandra/cassandra.json" }' 'http://localhost:80/package/repository/add'

echo Starting Portworx install from repository
curl -X POST --header 'Content-Type: application/vnd.dcos.package.install-request+json;charset=utf-8;version=v1'        --header 'Accept: application/vnd.dcos.package.install-response+json;charset=utf-8;version=v1'        -d ' {"packageName": "portworx", "packageVersion": "8688ecd-1.2.9", "appId": "/portworx"}' 'http://localhost:80/package/install'

echo Checking to see if Portworx REST api is available
URL="http://localhost:80/service/portworx/v1/px/status"
STATUS=$(curl --write-out %{http_code} --silent --output /dev/null "$URL")
COUNTER=1
while [ "$STATUS" -ne 200 -a $COUNTER -lt 20 ]
do
	STATUS=$(curl --write-out %{http_code} --silent --output /dev/null "$URL")
	echo $COUNTER Checking if Portworx REST endpoint is available.  Http status code: $STATUS
	COUNTER=$((COUNTER+1))
 	sleep 5
done
if [ "$STATUS" -ne 200 ]
then
	echo Portworx was not installed properly.  No 200 HTTP code.
	exit 1
fi

BODY_STATUS=$(curl -s http://localhost:80/service/portworx/v1/px/status/ | grep "Status" | head -n 1 | cut -c 3-8)
COUNTER=1
while [ "$BODY_STATUS" != "Status" -a $COUNTER -lt 50 ]
do
	BODY_STATUS=$(curl -s http://localhost:80/service/portworx/v1/px/status/ | grep "Status" | head -n 1 | cut -c 3-8)
	echo $COUNTER Checking if Portworx REST endpoint is returning status.
	COUNTER=$((COUNTER+1))
 	sleep 15
done
echo BODY_STATUS: $BODY_STATUS
if [ "$BODY_STATUS" != "Status" ]
then
	echo Portworx was not installed properly.  No Status returned.
	exit 1
fi

PORTWORX_STATUS=$(curl http://localhost:80/service/portworx/v1/px/status | jq '.Nodes[0].Status')
COUNTER=1
while [ "$PORTWORX_STATUS" -ne 2 -a $COUNTER -lt 50 ]
do
	PORTWORX_STATUS=$(curl http://localhost:80/service/portworx/v1/px/status | jq '.Nodes[0].Status')
	echo Portworx status $PORTWORX_STATUS
	COUNTER=$((COUNTER+1))
 	echo $COUNTER
 	sleep 15
done
if [ "$PORTWORX_STATUS" -ne 2 ]
then
	echo Portworx was not installed properly
	exit 1
fi
echo Portworx installed

echo Starting Cassandra install from repository
curl -X POST --header 'Content-Type: application/vnd.dcos.package.install-request+json;charset=utf-8;version=v1'        --header 'Accept: application/vnd.dcos.package.install-response+json;charset=utf-8;version=v1'        -d ' {"packageName": "cassandra-px", "packageVersion": "px-universe", "appId": "/cassandra-px"}' 'http://localhost:80/package/install'

echo Checking to see if Cassandra REST api is available
URL="http://localhost:80/service/cassandra-px/v1/endpoints/node"
STATUS=$(curl --write-out %{http_code} --silent --output /dev/null "$URL")
COUNTER=1
while [ "$STATUS" -ne 200 -a $COUNTER -lt 50 ]
do
	STATUS=$(curl --write-out %{http_code} --silent --output /dev/null "$URL")
	echo $COUNTER Checking if Cassandra REST endpoint is available.  Http status code: $STATUS
	COUNTER=$((COUNTER+1))
 	sleep 15
done
if [ "$STATUS" -ne 200 ]
then
	echo Cassandra was not installed properly.  No 200 HTTP code.
	exit 1
fi

BODY_STATUS=$(curl -s http://localhost:80/service/cassandra-px/v1/endpoints/node/ | grep "vips" | head -n 1 | cut -c 4-7)
COUNTER=1
while [ "$BODY_STATUS" != "vips" -a $COUNTER -lt 50 ]
do
	BODY_STATUS=$(curl -s http://localhost:80/service/cassandra-px/v1/endpoints/node/ | grep "vips" | head -n 1 | cut -c 4-7)
	echo $COUNTER Checking if Cassandra REST endpoint is returning vips.
	COUNTER=$((COUNTER+1))
 	sleep 15
done
echo BODY_STATUS: $BODY_STATUS
if [ "$BODY_STATUS" != "vips" ]
then
	echo Cassandra was not installed properly.  No vips returned.
	exit 1
fi

VIP=$(curl http://localhost:80/service/cassandra-px/v1/endpoints/node | jq '.vip')
echo Install Complete - Cassandra VIP: $VIP



