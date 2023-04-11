1. Create Network for Docker
```sh
# create network for kafka_sample
$ docker network create iot_network

# build docker-compose
$ docker-compose up -d

# check docker container
$ docker-compose ps

# check network
$ docker network inspect iot_network
```
