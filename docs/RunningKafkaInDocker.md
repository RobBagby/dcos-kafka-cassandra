# Running Kafka in Docker for Local Development
Installing Kafka on a local development machine is non-trivial.  A good option to consider is running Kafka locally in Docker.  It is no more complex than starting a container and takes literally seconds to spin up.  In this very short tutorial, you will learn how to run the Spotify Kafka container locally, as well as how to connect to it from another container within the same Docker network.  
You can find the full documentation here with many more details: ![https://github.com/spotify/docker-kafka] (https://github.com/spotify/docker-kafka).

## Networking
In the ![Running Cassandra in Docker for Local Development tutorial](RunningCassandraInDocker.md), we created a user-defined network and connected our Cassandra and cassandratester containers to it.  We will be conecting the Kafka container to the same network.  In case you are doing this tutorial first, we will include the instructions to create the user-defined network.  If you have already created the network, skip this step.

### Creating our User-defined network
```
docker network create sensor-network

docker network list
```
## Creating our Kafka Container
#### Docker for Windows  or Linux
```
docker run -d --name kafka -p 2181:2181 -p 9092:9092 --env ADVERTISED_HOST=172.30.0.1 --env ADVERTISED_PORT=9092 spotify/kafka

docker ps
```
You will notice that we mounted a volume by passing "-v".  Here we are mounting a directory on the host into the container.  In the Docker for Windows example, we have a directory C:\cassandradata on the windows machine.  That directory is being mounted to /var/lib/cassandra - the location where Cassandra persists its data, by default.  Remember that in Docker for Windows, you must share your C drive.
## Running our Test Container
I have written a very simple test container in python that you can use to test connectivity to your Cassandra cluster.  ![You can find the code here] (../cassandratester/src/cassandratester.py).  You do not have to build it.  I have an image in docker hub: rbagby/demo_cassandratester.
```
docker run --name cassandratester -d --env CASSANDRA_ADDRESS=localcassandra --env CASSANDRA_PORT=9042 --network=sensor-network rbagby/demo_cassandratester

docker logs -f cassandratester
```