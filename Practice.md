# Practice
로컬 환경에서 Docker를 이용하여 Kafka구성

* Document
https://kafka.apache.org/documentation/
* 실습
실습은 confluent platform을 이용하여 하도록 한다.
https://docs.confluent.io/platform/current/platform-quickstart.html#quick-start-for-cp

## Docker 환경구성
* 개요

* 네트워크 정의
  ```
  $ docker network create iot_network
  ```
* docker-compose.yml
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

* 컨테이너 작성 및 확인
  ```sh
  # 컨테이너 빌드
  $ docker-compse up -d

  # 확인
  $ docker-compose ps
  # 각 모듈 확인
  # broker (29092->29092/tcp, 9092->9092/tcp)
  # cli (9092/tcp)
  # zookeeper (2181/tcp, 2888/tcp, 32181->32181/tcp, 3888/tcp)
  ```

* 컨테이너 네트워크 정보 확인
  ```
  $ docker network inspect iot_network
  ```

## Kafka 기동
### topic 작성
* 컨테이너 확인
  ```s
  $ docker-compose ps
  ```  
* topic 작성
  ```s
  $ docker exec -it broker /bin/bash
  > kafka-topics --bootstrap-server broker:9092 --create --topic sample-topic --partition 3 replication-factor 1
  ```

* topic 확인
  ```s
  $ kafka-topics --bootstrap-server broker:9092 --describe --topic sample-topic
  ```

### Consumer 메지지 수신 설정
별도의 터미널을 연결해서 아래의 순서로 실행한다.
* cli 컨테이너 접속 & 메시지 수신 설정
  ```s
  $ docker exec -it cli /bin/bash
  # 메시지 수신 설정
  > kafka-console-consumer --bootstrap-server broker:29092 --topic sample-topic --group G1 --from-beginning
  ```

### Producer 메시지 송신 설정
별도의 터미널을 연결해서 아래의 순서로 실행한다.
* cli 컨테이너 접속 & 메시지 송신 설정
  ```s
  $ docker exec -it cli /bin/bash
  # 메시지 송신 설정
  > kafka-console-producer --broker-list broker:29092 --topic sample-topic
  ```

### Producer / Consumer 메시지 확인
* 메시지 송/수신 확인
  ```s
  # Producer 터미널
  /> kafka-console-producer --broker-list broker:29092 --topic sample-topic
  > Hello World
  > Good Good Good !!!
  -------------
  # Consumer 터미널
  /> kafka-console-consumer --bootstrap-server broker:29092 --topic sample-topic --group G1 --from-beginning
  > Hello world
  > Good Good Good !!!

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