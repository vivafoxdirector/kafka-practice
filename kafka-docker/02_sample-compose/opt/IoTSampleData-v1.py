import random
import json
import time
from datetime import date, datetime
from collections import OrderedDict
import argparse
import string
import pprint

from faker.factory import Factory
from kafka import KafkaProducer
from kafka import KafkaConsumer

# 참고사이트
# [Pythonメモ : fakerでテストデータを生成する](https://wonderwall.hatenablog.com/entry/2017/07/24/182522)
# [joke2k/faker](https://github.com/joke2k/faker)

# 터미널 작성을 위해서 Faker 사용
Faker = Factory.create
fake = Faker()
fake = Faker("ja_JP")

# IoT기기 더비 섹션(소문자 정의)
section = string.ascii_uppercase

# IoT기기 손신 Json 작성
def iot_json_data(count, proc):
    iot_items = json.dumps({
        'items': [{
            'id': i,                            # id
            'time': generate_time(),            # 데이터 생성 시간
            'proc': proc,                       # 데이터 생성 프로세스 : 프로그램실행시 파라메타
            'section': random.choice(section),  # IoT기기섹션 : A-Z문자을 랜덤 할당
            'iot_num': fake.zipcode(),          # IoT기기번호 : 우편번호을 랜덤 할당
            'iot_state': fake.prefecture(),     # IoT설치장소 : 지역명을 랜덤 할당
            'vol_1': random.uniform(100, 200),  # IoT값−1 : 100-200간의 값을 랜덤 할당(소수점이하, 14자리)
            'vol_2': random.uniform(50, 90)     # IoT값-2 : 50-90간의 값을 랜덤 할당(소수점이하, 14자리)
            } 
            for i in range(count)
        ]
    }, ensure_ascii=False).encode('utf-8')
    return iot_items


# IoT기기로 측적된 더미 더이터 생성시간
def generate_time():
    dt_time = datetime.now()
    gtime = json_trans_date(dt_time)
    return gtime

# date, datetime 변환 함수
def json_trans_date(obj):
    # 날짜형을 문자열로 변환
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    # 그외는 대상외
    raise TypeError ("Type %s not serializable" % type(obj))


# main : 터미널 출력 용
def tm_main(count, proc):
    print('터미널 출력')
    iotjsondata = iot_json_data(count, proc)
    json_dict = json.loads(iotjsondata)
    pprint.pprint(json_dict)


# main : Kafka출력용
def kf_main(count, proc):
    print('Kafka 출력')
    iotjsondata = iot_json_data(count, proc)
    json_dict = json.loads(iotjsondata)

    producer = KafkaProducer(bootstrap_servers=['broker:29092'])
    date = datetime.now().strftime("%Y/%m/%d")

    for item in json_dict['items']:
        # print(item)
        # result = producer.send('topic-01', json.dumps(item).encode('utf-8'))
        result = producer.send('topic-01', key=date.encode('utf-8'), value=json.dumps(item).encode('utf-8'))

    print(result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='IoT기기를 위한 더미데이터 생성')
    parser.add_argument('--count', type=int, default=10, help='데이터 작성건수')
    parser.add_argument('--proc', type=str, default='111', help='데이터 작성 프로세스명')
    parser.add_argument('--mode', type=str, default='tm', help='tm(터미널 출력) / kf(Kafka출력)')
    args = parser.parse_args()

    start = time.time()

    if (args.mode == 'kf'): 
        kf_main(args.count, args.proc)
    else :
        tm_main(args.count, args.proc)

    making_time = time.time() - start

    print("")
    print(f"데이터 작성건수:{args.count}")
    print("데이터 작성시간:{0}".format(making_time) + " [sec]")
    print("")