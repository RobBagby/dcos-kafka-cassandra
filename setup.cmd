docker build -t rbagby/demo_base .
docker build -t rbagby/demo_producer producer
docker build -t rbagby/demo_consumer consumer
docker build -t rbagby/demo_lagreader lagreader