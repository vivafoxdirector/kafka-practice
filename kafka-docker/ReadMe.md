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
  ```s
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
  ```s
  $ docker network inspect iot_network
  ```

## Kafka 기본기동
1. topic 작성
2. Consumer 작성
3. Producer 작성
4. Consumer & Producer 메시지 송수신 확인
![구성도](./assets/practice1.avif)

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

## Kafka 응용
위 기본적인 동작을 기반으로 응용하는 방법에 대해서 알아본다.
![구성도](./assets/practice2.avif)

### 토픽 작성
```s
# 토픽 "topic-01" 생성
$ docker exec -it broker /bin/bash
/> kafka-topics --bootstrap-server broker:9092 --create --topic topic-01 --partitions 3 replication-factor 1

# 토픽 확인
/> kafka-topics --bootstrap-server borker:9092 --describe --topic topic-01
```

### Producer 컨테이너 작성
1. Producer 디렉토리 구조
새롭게 Producer 작성하고, Python프로그램 가동 컨테이너로 구성하도록 한다.
```s
$ tree
.
├─ Dockerfile
├─ docker-compose.yml
├─ opt
│    └─ IoTSampleDate-v2.py
└─ requirements.txt
```

2. docker-compose.yml 작성
```s
version: '3'
services:
  iot:
    build: .
    working_dir: '/app/'
    tty: true
    volumes:
      - ./opt:/app/opt

networks:
  default:
    external:
      name: iot_network

```

3. DockerFile 작성
```s
FROM python:3.7.5-slim
USER root

RUN apt-get update
RUN apt-get -y install locales && localedef -f UTF-8 -i ko_KR ko_KR.UTF-8

ENV LANG ko_KR.UTF-8
ENV LANGUAGE ko_KR:ko
ENV LC_ALL ko_KR.UTF-8
ENV TERM xterm

# 이거 설정 안하면 docker-compose build 시 "No such file or directory" 오류 발생됨
# http://pixelbeat.jp/could-not-open-requirements-file-with-docker-using-python/
COPY requirements.txt .

RUN apt-get install -y vim less
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt
```

3. requirements.txt 작성
```s
faker
kafka-python
```

### Producer 컨테이너 작성 및 확인
1. 컨테이너 기동
```s
# 기동
$ docker-compose up -d

# 확인
$ docker-compose ps

# 모든 컨테이너 확인
$ docker ps 
```

### Consumer 메시지 수신 설정
1. Consumer 설정
```s
# cli 컨테이너 접속
$ docker exec -it cli /bin/bash
/>

# Consumer로서 메시지 수신 설정
/> kafka-console-consumer --bootstrap-server broker:29092 --topic topic-01 --group G1 --from-beginning
```

### Producer 메소지 송신
- Producer 기동시키고 데이터 생성 프로그램을 작성한다. OSS인 [Faker](https://github.com/joke2k/faker)라이브러리를 이용하여 Json 형태의 더미 데이터를 생성하는 Python프로그램을 작성한다.
- 소스 : [IotSampleData-v1.py](./kafka-docker/opt/IotSampleData-v1.py)

- 더미 데이터 생성해서 송신하기 위해서 별도의 터미널에서 Producerr에 접속하여 프로그램을 기동한다.
  ```s
  $ docker exec -it iotsampledata_iot_1 /bin/bash
  /> cd /app/opt
  /> python IoTSampleData-v1.py --mode kf
  ```
- Consumer 프롬프트에서 Producer가 송신한 메시지를 확인한다.

## Kafka의 KSQL 적용
KSQL을 사용해서 Producer가 송신한 데이터를 특정 조건을 부여하여 추출하는 예제를 만들도록 한다.
간단한 구성도는 아래와 같다.
![구성도](./assets/practice3.avif)

### KSQL컨테이너 작성
앞서 작성한 docker-compose.yaml에 ksql-server(KSQL서버)와 ksql-cli(KSQL클라이언트) 컨테이너 정의를 추가한다.



# 참조사이트
## 강좌(20230327)
1. 아키텍처 & 튜닝포인트
- [Apache Kafkaの概要とアーキテクチャ](https://qiita.com/sigmalist/items/5a26ab519cbdf1e07af3)
- [아키텍처문서PDF](https://www.ospn.jp/osc2017.enterprise/pdf/OSC2017.enterprise_Hitachi_Kafka.pdf)

2. 실습
- [KafkaをローカルのDocker環境で、さくっと動かしてみました 　第１回](https://qiita.com/turupon/items/12268ddb95ecd7b7ae07)
- [KafkaをローカルのDocker環境で、さくっと動かしてみました 　第２回](https://qiita.com/turupon/items/59eb602766a38bc3b621)

- [Apache Kafkaとは](https://zenn.dev/gekal/articles/kafka-env-for-local-developmen-use-docker-compose)

3. 더미데이터(테스트 데이터)
- [Pythonメモ : fakerでテストデータを生成する](https://wonderwall.hatenablog.com/entry/2017/07/24/182522)
- [joke2k/faker](https://github.com/joke2k/faker)

## 트러블슈팅
1. Docker-compose build 시 "no such file or directory"발생시 대응
- [[Docker/Python]Could not open requirements file: [Errno 2] No such file or directory: でDocker buildに失敗したときの対処法](http://pixelbeat.jp/could-not-open-requirements-file-with-docker-using-python/)