# Running Cassandra in Docker for Local Development
Installing Cassandra on a local development machine is non-trivial.  A good option to consider is running Cassandra locally in Docker.  It is no more complex than starting a container and takes literally seconds to spin up.  In this very short tutorial, you will learn how to run the official Cassandra container locally, as well as how to connect to it from another container within the same Docker network.  
You can find the full documentation here with many more details: ![https://hub.docker.com/_/cassandra/] (https://hub.docker.com/_/cassandra/).

## Networking
You need to have network connectivity in order to connect to Cassandra.  While the documentation on Docker Hub illustrates using container links, you should not use them.  ![They are depricated and may be removed] (https://docs.docker.com/engine/userguide/networking/default_network/dockerlinks/).  

A better idea is to use user-defined networks when you want to control which containers can communicate with each other.  In our simple demo we will create a user-defined network called "sensor-network" and we will connect our Cassandra container, as well as our test application to that network.
### Creating our User-defined network
You can create bridge, overlay, as well as many network types.  For full dockumentation, see the ![Docker documentation here] (https://docs.docker.com/engine/userguide/networking/#user-defined-networks).  In our case we will create a bridge network.
```
docker network create sensor-network

docker network list
```
## Creating our Cassandra Container
#### Docker for Windows
```
docker run -d --name localcassandra --network=sensor-network -p 9042:9042 -v  C:/cassandradata:/var/lib/cassandra cassandra:3.10

docker ps
```
#### Linux
```
docker run -d --name localcassandra --network=sensor-network -p 9042:9042 -v  /src/cassandradata:/var/lib/cassandra cassandra:3.10

docker ps
```
You will notice that we mounted a volume by passing "-v".  Here we are mounting a directory on the host into the container.  In the Docker for Windows example, we have a directory C:\cassandradata on the windows machine.  That directory is being mounted to /var/lib/cassandra - the location where Cassandra persists its data, by default.  Remember that in Docker for Windows, you must share your C drive.
## Running our Test Container
I have written a very simple test container in python that you can use to test connectivity to your Cassandra cluster.  ![You can find the code here] (../cassandratester/src/cassandratester.py).  You do not have to build it.  I have an image in docker hub: rbagby/demo_cassandratester.
```
docker run --name cassandratester -d --env CASSANDRA_ADDRESS=localcassandra --env CASSANDRA_PORT=9042 --network=sensor-network rbagby/demo_cassandratester

docker logs -f cassandratester
```