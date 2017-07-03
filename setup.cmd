docker build -t rbagby/demo_base .
docker build -t rbagby/demo_consumer simpleconsumer
docker build -t rbagby/demo_producer simpleproducer
docker build -t rbagby/demo_lagreader lagreader