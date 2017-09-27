# Running Kafka in Docker for Local Development
Installing Kafka on a local development machine is non-trivial.  A good option to consider is running Kafka locally in Docker.  It is no more complex than starting a container and takes literally seconds to spin up.  In this very short tutorial, you will learn how to run the Spotify Kafka container locally.  
You can find the full documentation of the Spotify Kafka image here with many more details: ![https://github.com/spotify/docker-kafka] (https://github.com/spotify/docker-kafka).

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
You will notice the ADVERTISED_HOST was set to an IP address.  This should be the IP address of the host.  All of the other settings you should not need to change, with the possible exception of the name of the container instance.