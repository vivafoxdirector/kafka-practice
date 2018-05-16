# Kafka-practice

## Apache Kafka??
*2011년에 LinkedIn에서 공개된 오픈소스이다. Apache Kafka는 **분산 메시징 시스템**이라 한다. Kafka는 웹서비스등에서 발생되는 대용량 데이터(e.g., 로그나 이벤트 데이터)를 High ThroughPut / Low Latency 상태에서 수집 및 전송하는 기능을 하도록 개발되었다 한다.*

공식 홈페이지에 기되어 있는 SalesPoint는 아래와 같다.
* Fast
어쨓든 대용량 메시지를 다루는 것이 가능하다.
* Scalable
Kafka는 싱글클러스터로 큰 규모의 메시지를 다룰 수 있고 **다운 타임없이** 유연하고 투과적으로 스케일할 수 있다.
* Durable
메시지는 파일형태로 디스크에 저장되고, 각각의 클러스터내에 복제되어 작성되기 때문에 데이터의 유실을 예방한다. (성능에 영향없이 테라 바이트급 메시지를 다룰 수 있다)
* Distributed by Design
클러스터는 안정성있게 설계되어 있다.(耐障害性)

## 어디에 사용되나
[Use Cases](http://kafka.apache.org/documentation.html#uses)로서 메시지큐나 웹사이트 액티비티 트래킹(LinkedIn의 Use Case) 메트릭스나 로그 수집, [Storm](https://storm.apache.org/)이나 [Samza](http://samza.apache.org/)를 사용한 스트림처리등에서 사용된다.

Twitter, Netflix, Square, Spotify, Uber등의 기업에서 사용하고 있다.(cf. [Powered By](https://cwiki.apache.org/confluence/display/KAFKA/Powered+By]))

## Kafka의 초기
Kafka 디자인을 이해하기 위해서는 LinkedIn에서 왜 Kafka가 필요하게 되었는지 알아볼 필요가 있다. 이에 대해서는 2012년 IEEE의 논문 "[Building LinkedIn's Real-time Activity Data Pipeline](http://sites.computer.org/debull/A12june/pipeline.pdf)"을 읽어보면 알수있는데, 여기서 간략하게 정리하면 아래와 같다.

LinkedIn에서는 크게 2가지 데이터를 다루고 있다. 1번째는 웹사이트에서 수집된 대량의 유저 엑티비티 데이터이다. 이 데이터는 Hadoop(배치 처리)을 통해서 기계학습하고 추천/뉴스피드등 서비스 개선에 사용하고 있다. 이뿐만이 아니라 이러한 데이터는 서비스 감시(시큐리티 등)에도 사용된다. 2번째는 시스템 로그등을 리얼타임으로 처리하여 서비스 모니터링을 위해 사용된다. 이부분은 최근 웹서비스에서 많이 사용되어 지고 있다.

문제는 각각의 데이터가 지나는 길은 하나뿐이라는 것. 액티비티 데이터는 배치 처리로 특화되어 있기 때문에 리얼타임처리를 할 수 없다. 결국 서비스 감시에는 지연이 발생될 수밖에 없었다. 그리고 시스템로그는 리얼타임처리에 특화되어 있기 때문에 장기간에 걸쳐서 Capacity Planing이나 시스템 디버그에는 사용할 수 없었다. 서비스를 개선하기 위해서는 각각의 타입이 다른 데이터피드를 최소한의 비용으로 통합할 수 있도록 해야 했다. 그리고 LinkedIn에서 사용되어 지는 데이터가 비지니스의 핵심이 되는 기업에서는 그 데이터를 여러 부서나 팀에서 간단하게 이용할 수 있어야 했다.

이러한 문제를 해결하기 위해 큰 볼륨을 가지는 여러형태의 데이터를 수집하고 여러 형태의 시스템(배치/리얼타임)에서 데이터를 읽을 수 있도록 하는 통일된 메시지 플랫폼 구축이 시작되었다.

처음에는 기존 메시지 시스템(논문에는 ActiveMQ을 테스트해봄)상에 구축하려고 하였다. 그러나 Production 레벨의 데이터를 처리할 때 아래와 같은 문제가 발생되었다.

* 병열로 큐 메시지를 읽을 때 메시지마다 누가 읽었는지를 기록해야 하는 기능(Mutex)이 있었다. 이때문에 대량의 데이터를 다루게 되면 메모리가 부족하게되는 현상이 생겼다. 메모리가 부족하게 되면 대량의 Ramdom IO가 발생되어 성능(Performance)에 심각한 영향을 주게 된다.
* 배치 처리/리얼타임처리 양쪽에서 큐를 읽어들일때 적어도 2개의 데이터를 복사가 이루어지게 되어 비효율적이었다.

이와 같은 문제에서 새로운 메시지 시스템인 Kafka가 나오게 된 배경이 된다.
Kafka가 목적으로 하는 것은 아래와 같다.
* 여러종류의 데이터/대용량 데이터를 통일적으로 다룬다.
* 여러 형태의 시스템(배치/리얼타임)이 같은 데이터를 읽도록 한다.
* High ThroughPut으로 데이터를 처리한다.(병렬로 데이터를 읽는다.)

## 어떻게 동작하는가?
Kafka는 Broker(클러스터), Producer, Consumer라는 3가지 컴포넌트로 구성된다. Producer는 메시지 전송을 담당하고 Consumer는 메시지를 구독하고, 그리고 Kafka의 핵심 코어에 해당하는 Broker는 클러스터를 구성하고 Producer와 Consumer 중간에서 메시지를 송수신하는 큐로서 동작 한다.
<center>![Kafka](http://kafka.apache.org/images/producer_consumer.png)</center>
<center>http://kafka.apache.org/images/producer_consumer.png</center>

### 메시지 송수신
Kafka는 Topic을 통해서 메시지 송수신을 한다. Topic이란 메시지 피드와 같은 것이다. 예를 들어 검색에 관련된 데이터를 "Search"라는 Topic명으로 Broker에 보내두고 검색에 관련된 데이터를 원하는 Consumer는 "Search"라는 Topic명을 사용하여 Broker로부터 구독을 한다.

### Pull vs Push
Broker가 Consumer에 데이터를 Push하는 경우(fluentd, logstash, flume) 또는 Consumer가 Broker로 부터 데이터를 Pull하는 경우는 메시지 시스템 디자인에 큰 영향을 주게 된다. 물론 각각의 Pros/Cons는 있다. Kafka는 Pull타입의 Consumer를 채용하고 있다. 이유는 아래와 같다.

* Push라면 수많은 Consumer를 상대하기 어렵고, Broker가 데이터 전송량등을 의식하지 않으면 안된다. Kafka의 목적은 최대한 빠르게 데이터를 소비하는 것이다. (예기치 않은 접근등)전송량을 의식하지 않게 되면 실제 Consumer수보다 많은 수의 Consumer에게 메시지를 보내게 되는 경우가 발생 된다. Pull로 하게 되면 Consumer가 소비량을 Consumer자신이 관리할 수 있다.

* Pull이면 배치 처리에도 사용될 수 있다. Push로 하게 되면 어느정도 처리된 데이터를 Consumer가 받을수 있는지 없는지에 관계없이 전송하지 않으면 안된다.

* Pull에서 한가지 생각해야 하는 부분은 Broker에 데이터가 아직 도달하지 않은 상태의 비용이지만 이는 long polling이라는 기능으로 대응이 가능하다.

### 메시지 라이프 사이클
Broker는 Consumer가 메시지를 구독했는지에 관계없이 설정된 기간동안만 저장하고 이후 삭제한다. 이것은 Kafka의 주요 특징중 하나이다. 예를 들어 보존기간을 2일로 설정하면 메지시 전달하고 나서 데이터는 2일동안 저장상태가 된다.(이후 삭제)
이 때문에 Consumer쪽에서 메시지를 어느정도 읽었는지 Consumer가 관리한다.(Broker는 관리할 필요 없다) 보통순차적으로 메시지를 읽어들이는데 Consumer에 문제가 생겼을때 읽은 위치를 되돌려 복구하도록 하는 기능을 가지고 있다. (최악의 경우 어느정도 Consumer를 복구할 수 있는지에 따라 데이터의 저장기간이 결정되고 데이터사이즈도 결정된다.)
이러한 특징으로 Consumer는 Broker에도 다른 Broker에도 큰 영향을 주지 않는다.

## 고속으로 메시지를 소비
Kafka의 재미있는 기능은 Consumer가 Broker로 부터 고속으로 메시지를 전달받는 것이다. 이부분은 어떻게 동작이 되는지 설명한다.

### 병렬로 큐를 읽는것은 위험
고속으로 메시지를 소비하기 위해서는 Broker의 데이터를 병렬로 읽을 필요가 있다. 하나 이상의 Consumer가 병렬로 큐를 읽어들이는 것은 위험하다.

* 중복없이 메시지를 송신하기 위해서는 메시지마다 어느 Consumer에 보낼것인지를 관리할 필요가 있다.

* 큐에 메시지를 저장하기 까지는 순서를 보장할 수 있지만 병렬로 읽어들이게 되면 하나 이상의 Consumer에 소비되는 순간 순서를 잃게 된다.

Kafka의 설계는 이를 해결하도록 구현되었다.

### Broker에서 메시지 저장
먼저 Broker의 메시지 보존방법에는 특징이 있다. Kafka는 Topic마다 1개 이상의 Partition이라는 단위로 메시지를 저장한다. 메시지는 각각의 Partition의 말미(꼬리)에 추가 된다. 이렇게 하여 Partition마다 메시지 순서를 보증하게 된다. 아래 그림에는 하나의 Topic에 3개의 Partition이 있고 각 Partition에 메시지가 저장되는 것을 나타내고 있다.
<center>![Partition](http://kafka.apache.org/images/log_anatomy.png)</center>
<center>http://kafka.apache.org/images/log_anatomy.png</center>

### Partition 동작
Partition에는 크게 2가지 목적을 가지고 있다.
* 여러 서버로 메시지를 분산시키기 위해(하나의 서버용량을 초과한 메시지를 저장할 수 있다)
* 병렬처리를 하기 위해

어떤식으로 병렬처리를 할까? Consumer는 그룹단위로 메시지를 구족한다. 그리고 "하나의 Partition데이터는 하나의 Consumer그룹내의 하나의 Consumer에만 소비하도록 한다"라는 제한으로 이것을 실현한다.(즉, Consumer병렬수는 Partition수를 초과하지 않는다.) 아래 그림은 2개의 Consumer그룹 A와 B에 속하는 복수개의 Consumer가 병렬로 메시지를 구독하고 있는 형태이다. 그룹내에서는 병렬처리하지만 그룹간에는 전통적인 방법인 Pub/Sub모델(1대1)처럼 보인다.
<center>![Consumer Group](http://kafka.apache.org/images/consumer-groups.png)</center>
<center>http://kafka.apache.org/images/consumer-groups.png</center>

이런 구조는 아래와 같은 이점을 가진다.
* 어떤 Partition을 읽는 Consumer는 1개이기 때문에 메시지가 누구에게 어디까지 읽었는지 기록할 필요없이 단순하게 어디까지 읽었는지를 통지하면 된다.
* 읽고 있는 Consumer는 1개이기 때문에 Consumer는 lazy하게 읽은 부분을 기록해두면 되기 때문에 처리에 실패하더라도 다시 읽을수 있게 된다.(at-least-once)
* 어느 메시지가 읽어들였는지를 lazily에 기록할 수 있기 때문에 성능을 보장할 수 있다.(Partition의 주체가 결정되지 않는 경우 직접 Consumer를 할당하거나 아니면 랜덤하게 Consumer를 로드밸런스할 수 밖에 없다. 랜덤하게 하면 복수의 프로세스가 동시에 같은 Partition을 구독하게되므로 mutex가 필요하게 되고 이때문에 Broker처리가 무겁게 된다.)

### 순서성 관련해서 한마디 더
Partition내, 즉 Consumer내에서는 순서가 보장된다. 결국 Broker에 기록된 순서로 소비된다. 하지만 Partition간에는 보장하지 않는다.

Producer는 Broker에 메시지를 전달할 때에 Key를 지정할 수 있다. 이 Key를 이용하여 같은 Key로 지정된 메시지를 같은 Partition에 저장할 수 있다. Partition내에 순서성과 Key를 이용하면 대체적으로 어플리케이션에는 문제가 없다는 의미이다. 완전한 순서성을 확보하고 싶다면 Partition을 하나로 하면 된다. (Consumer도 하나로 해야하나..)

## High ThroughPut을 향해
Broker로의 읽기(수신)/쓰기(송신)는 어쨓든 빠르다. LinkedIn 벤치마크에 의하면 200만write/sec ([Benchmarking Apache Kafka: 2 Million Writes Per Second (On Three Cheap Machines](https://engineering.linkedin.com/kafka/benchmarking-apache-kafka-2-million-writes-second-three-cheap-machines))라는 결과가 나왔다. 왜이렇게 빠른가는 아래의 2가지 구현 사상으로 실현된다.

* write
버퍼에 쓰기는 주체는 커널의 메모리 캐시를 충분히 끌어다 사용한다.(Broker가 동작하고 있는 서버 메모리 32기가 중 28~30기가를 캐시로 사용된다.)
* read
페이지 캐시로부터 네트워크 socket에 효과적으로 데이터를 건네주기 위해 sendfile()을 사용한다.

## 정리
앞서 소개한 논문 "[Building LinkedIn’s Real-time Activity Data Pipeline](http://sites.computer.org/debull/A12june/pipeline.pdf)"에는 별도로 Kafka의 재미있는 부분도 많이 기술되어 있기 때문에 Kafka를 사용하려는 사람은 꼭한번 읽어보시라...

## ref
* Apache Kafka 입문
  * https://deeeet.com/writing/2015/09/01/apache-kafka/
* GO로 KAFKA
  * https://github.com/vsouza/go-kafka-example
* 사용하기
  * https://www.cakesolutions.net/teamblogs/getting-started-with-kafka-using-scala-kafka-client-and-akka
  * https://gist.github.com/fancellu/f78e11b1808db2727d76
  * https://adtech.cyberagent.io/scalablog/2015/07/17/kafka%E3%82%92%E4%BD%BF%E3%81%A3%E3%81%A6%E3%83%81%E3%83%A3%E3%83%83%E3%83%88%E3%83%84%E3%83%BC%E3%83%AB%E3%82%92%E4%BD%9C%E3%81%A3%E3%81%A6%E3%81%BF%E3%81%BE%E3%81%97%E3%81%9F/
  * https://qiita.com/bwtakacy/items/d1345e10d2adbd4b4431
  * https://qiita.com/ttsubo/items/3ae7ee8b34bb62879613
