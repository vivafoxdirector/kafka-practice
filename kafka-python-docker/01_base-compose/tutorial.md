1. Create Network for Docker
```sh
# docker compose install
$ sudo apt-get update
$ sudo apt-get install docker-compose-plugin

# create network for kafka_sample
$ docker network create iot_network

# build docker-compose
$ docker compose up
# $ docker-compose up -d # old version

# check docker container
$ docker compose ps
# $ docker-compose ps

# check network
$ docker network inspect iot_network
```
