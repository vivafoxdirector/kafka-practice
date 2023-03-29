# Practice
로컬 환경에서 Docker를 이용하여 Kafka구성

* Document
https://kafka.apache.org/documentation/
* 실습
실습은 confluent platform을 이용하여 하도록 한다.
https://docs.confluent.io/platform/current/platform-quickstart.html#quick-start-for-cp

## 실습환경 구성
1. 개요

2. 네트워크 정의
```
$ docker network create iot_network
```
3. docker-compose.yml
* 참조
https://github.com/confluentinc/cp-all-in-one/blob/7.3.2-post/cp-all-in-one/docker-compose.yml
https://docs.confluent.io/platform/current/platform-quickstart.html#prerequisites
https://hub.docker.com/r/obsidiandynamics/kafka

```yml
version: "3"
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:5.5.1
    hostname: zookeeper
    container_name: zookeeper
    ports:
      - "32181:32181"
    environment:
      ZOOKEEPER_CLIENT_PORT: 32181
      ZOOKEEPER_TICK_TIME: 2000

  broker:
    image: confluentinc/cp-kafka:5.5.1
    hostname: broker
    container_name: broker
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
      - "29092:29092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: "zookeeper:32181"
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://broker:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      CONFLUENT_SUPPORT_METRICS_ENABLE: "false"

  cli:
    image: confluentinc/cp-kafka:5.5.1
    hostname: cli
    container_name: cli
    depends_on:
      - broker
    entrypoint: /bin/sh
    tty: true

networks:
  default:
    external:
      name: iot_network
```


# 참조사이트
## 강좌(20230327)
1. 아키텍처 & 튜닝포인트
- [Apache Kafkaの概要とアーキテクチャ](https://qiita.com/sigmalist/items/5a26ab519cbdf1e07af3)
- [아키텍처문서PDF](https://www.ospn.jp/osc2017.enterprise/pdf/OSC2017.enterprise_Hitachi_Kafka.pdf)

2. 실습
- [KafkaをローカルのDocker環境で、さくっと動かしてみました 　第１回](https://qiita.com/turupon/items/12268ddb95ecd7b7ae07)
- [KafkaをローカルのDocker環境で、さくっと動かしてみました 　第２回](https://qiita.com/turupon/items/59eb602766a38bc3b621)

- [Apache Kafkaとは](https://zenn.dev/gekal/articles/kafka-env-for-local-developmen-use-docker-compose)