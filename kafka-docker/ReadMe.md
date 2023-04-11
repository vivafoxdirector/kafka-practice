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
  > kafka-topics --bootstrap-server broker:9092 --create --topic sample-topic --partitions 3 replication-factor 1
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
COPY ./opt/IoTSampleDate-v2.py /app/opt

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
- 소스 : [IotSampleData-v1.py](./02_sample-compose/opt/IotSampleData-v1.py)

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

1. docker-compose.yml 작성
```s
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

  ksql-server:
    image: confluentinc/cp-ksql-server:5.4.3
    hostname: ksql-server
    container_name: ksql-server
    depends_on:
      - broker
    ports:
      - "8088:8088"
    environment:
      KSQL_CONFIG_DIR: "/etc/ksql"
      KSQL_LOG4J_OPTS: "-Dlog4j.configuration=file:/etc/ksql/log4j-rolling.properties"
      KSQL_BOOTSTRAP_SERVERS: "broker:29092"
      KSQL_HOST_NAME: ksql-server
      KSQL_APPLICATION_ID: "IoT-demo-1"
      KSQL_LISTENERS: "http://0.0.0.0:8088"
      KSQL_CACHE_MAX_BYTES_BUFFERING: 0
      KSQL_AUTO_OFFSET_RESET: "earliest"

  ksql-cli:
    image: confluentinc/cp-ksql-cli:5.4.3
    container_name: ksql-cli
    volumes:
      - $PWD/ksql.commands:/tmp/ksql.commands
    depends_on:
      - broker
      - ksql-server
    entrypoint: /bin/sh
    tty: true

networks:
  default:
    external:
      name: iot_network 
```

2. 컨테이너 작성 및 확인
```s
# 컨테이너 작성 실행
$ docker-compose up -d

# 컨테이너 확인
$ docker-compose ps
```

### 추상데이터를 스트리밍하기 위한 topic 작성
1. broker 접속
```s
$ docker exec -it broker /bin/bash
```
2. 추출데이터를 스트리밍을 위한 topic[topic-11] 작성 및 확인
```s
# topic 작성
/> kafka-topics --bootstrap-server broker:9092 --create --topic topic-11 --partitions 3 replication-factor 1

# 전체 topic 확인
/> kafka-topics --bootstrap-server broker:9092 --list

# 특정 topic 확인
/> kafka-topics --bootstrap-server broker:9092 --describe --topic topic-11
```

### KSQL으로 스트리밍 작성
1. ksql-cli 접속
```s
$ docker exec -it ksql-cli /bin/bash
```

2. ksql-cli에서 ksql-server로 접속
```s
# SSL이 사용하지 않는 경우
/> ksql http://ksql-server:8088

# SSL을 사용하는 경우
/> ksql https://ksql-server:8088
```

3. Producer 에서 전송된 데이터(topic-01)의 스트림(topic01_stream1) 작성
```s
# topic01_stream1 작성
ksql> 
CREATE STREAM topic01_stream1 (
  id INT, 
  time VARCHAR, 
  proc VARCHAR, 
  section VARCHAR, 
  iot_num VARCHAR, 
  iot_state VARCHAR, 
  vol_1 DOUBLE, 
  vol_2 DOUBLE
) WITH (KAFKA_TOPIC = 'topic-01', VALUE_FORMAT='JSON', KEY='section');

# topic01_stream1 정보 확인
ksql> describe extended topic01_stream1;

# (topic01_stream1)의 스트림 데이터를 아래의 조건으로 추출하고, 그 결과를 topic-11로 송신하는 스트림 (topic01_stream2)을 작성한다.
# 추출조건: section='E' OR section='C' OR section='W'
ksql> 
CREATE STREAM topic01_stream2 
WITH (KAFKA_TOPIC = 'topic-11', VALUE_FORMAT='JSON') AS 
  SELECT 
    t01s1.section as section, 
    t01s1.time as time, 
    t01s1.proc as proc, 
    t01s1.iot_num as iot_num, 
    t01s1.iot_state as iot_state, 
    t01s1.vol_1 as vol_1, 
    t01s1.vol_2 as vol_2 
  FROM topic01_stream1 t01s1 
  WHERE section='E' OR section='C' OR section='W';

# topic01_stream2 정보 확인
ksql> describe extended topic01_stream2;

# 작성된 스트림과 topic 관계 정보 확인
ksql> show streams;
```

### KSQL으로 스트리밍 확인
1. topic01_stream2 로 스트림되는 정보를 확인하기 위한 설정
```s
ksql> select * from topic01_stream2 emit changes;
```
=> producer에서 추출데이터를 수신대기 상태가 된다.

2. 별도의 터미널로 Producer에 접속을 하고, 앞서 작성한 python프로그램을 실행한다.
```s
$ docker exec -it iotsampledata_iot_1 /bin/bash
/> cd /app/opt
/> python IotSampleData-v1.py --mode kf --count 30
```

3. ksql 프롬프트에 Producer가 보낸 메시지가 추출된 형태로 표시되는지 확인
```s
ksql> select * from topic01_stream2 emit changes;
```

## KSQL에서 추출한 데이터를 수신하는 Consumer를 Python으로 기동
![구성도](./assets/practice4.avif)
- [KafkaをローカルのDocker環境で、さくっと動かしてみました 　第５回](https://qiita.com/turupon/items/bd27834a42dda865469d)

### Consumer 컨테이너 작성
topic-11에서 추출한 데이터를 수신하기 위해서 새롭게 Consumer컨테이너를 작성한다.
1. 컨테이너 구성도
```s
$ tree
.
├─ Dockerfile
├─ docker-compose.yml
├─ opt
│   └ IoTTpicData-v1.py
└─ requirements.txt
```

2. docker-compose.yml
```yml
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

3. Dockerfile
```yml
FROM python:3.7.5-slim
USER root

RUN apt-get update
RUN apt-get -y install locales && localedef -f UTF-8 -i ko_KR ko_KR.UTF-8

ENV LANG ko_KR.UTF-8
ENV LANGUAGE ko_KR:ko
ENV LC_ALL ko_KR.UTF-8
ENV TERM xterm

COPY requirements.txt .
#WORKDIR /app/opt

RUN apt-get install -y vim less
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
#RUN ls -la /app/opt
RUN pip install -r requirements.txt
```

4. requirements.txt
```
kafka-python
```

### Cosumer 컨테이너 작성 및 확인
```s
# 컨테이너 빌드
$ docker-compose up -d
creating ...

# 컨테이너 확인
$ docker-compose ps

# 모든 컨테이너 확인
$ docker ps
```

### Consumer에서 기동되는 프로그램 작성
지금까지 작성한 토픽등을 정리해본다. 토픽 topic-01을 생성하고, Producer역할을 하는 Python을 이용하여 topic-01에 송신하는 프로그램을 작성하였다.
그리고, KSQL을 통해서 topic-01의 내용을 특정 내용을 필터하여 다시 topic-11로 전송하는 환경도 구성하였다. 즉, 정리하면 아래와 같은 구성이 된다.

[Producer]Python -> [Topic]Topic-01 -> KSQL -> [Topic]Topic-11 -> [Consumer]Python

위 구성에서 [Consumer]Python을 작성하고 소스는 아래를 참조한다.
- 소스 : [IotSampleData-v1.py](./03_sample-compose/opt/IotSampleData-v1.py)

### Consumer메시지 수신 설정
데이터를 수신받기 위해 Consumer에 접속하여 프로그램 디렉토리로 이동한다.
```s
# Consumer 컨테이너 이동
$ docker exec -it iottopicdata_ktp_1 /bin/bash
/>

# Python 실행
/> cd /app/opt/
/> python IotTopicData-v1.py --mode tm
# 데이터 수신을 기다리는 상태가 된다.
```

### Producer 메시시 송신 
데이터를 송신하기 위해 별도의 터미널을 기동해서, Producer에 접속하고, Python 프로그램이 있는 디렉토리로 이동
```s
$ docker exec -it IoTSampledata_iot_1 /bin/bash
# Python 실행, 생성 데이터 송신한다.
/> cd /app/opt
/> python IoTSampleData-v1.py --mode kf --count 30
```

### 확인
Consumer 프롬프트에서 Producer가 송신한 데이터가 표시되는 것을 확인한다.
```s
# 아래는 위 Consumer에서 실행된 상태
/> python IoTTopicData-v1.py --mode tm  
# 아래 Producer 에서 전송된 메시지 출력된다.
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

3. 더미데이터(테스트 데이터)
- [Pythonメモ : fakerでテストデータを生成する](https://wonderwall.hatenablog.com/entry/2017/07/24/182522)
- [joke2k/faker](https://github.com/joke2k/faker)

## 트러블슈팅
1. Docker-compose build 시 "no such file or directory"발생시 대응
- [[Docker/Python]Could not open requirements file: [Errno 2] No such file or directory: でDocker buildに失敗したときの対処法](http://pixelbeat.jp/could-not-open-requirements-file-with-docker-using-python/)


├
─
└
│

