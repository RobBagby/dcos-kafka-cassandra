docker build -t rbagby/demo_base .
docker build -t rbagby/demo_producer producer
docker build -t rbagby/demo_consumer consumer
docker build -t rbagby/demo_lagreader lagreader
docker build -t rbagby/demo_cassandratester cassandratester
docker build -t rbagby/webapi webapi
docker build -t rbagby/web web