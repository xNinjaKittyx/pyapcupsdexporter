#!/usr/bin/python
import os
import time

from apcaccess import status as apc
from influxdb import InfluxDBClient

hostname = os.getenv('HOSTNAME', 'apcupsd-influxdb-exporter')
dbname = os.getenv('INFLUXDB_DATABASE', 'apcupsd')
user = os.getenv('INFLUXDB_USER')
password = os.getenv('INFLUXDB_PASSWORD')
port = os.getenv('INFLUXDB_PORT', 8086)
host = os.getenv('INFLUXDB_HOST', 'localhost')
client = InfluxDBClient(host, port, user, password, dbname)

client.create_database(dbname)

while True:
    ups = apc.parse(apc.get(host=os.getenv('APCUPSD_HOST', 'localhost')), strip_units=True)

    if os.environ['WATTS']:
        ups['NOMPOWER'] = os.getenv('WATTS')

    watts = float(ups['NOMPOWER']) * 0.01 * float(ups['LOADPCT'])
    json_body = [
        {
            'measurement': 'apcaccess_status',
            'fields': {
                'WATTS': watts,
                'LOADPCT': float(ups['LOADPCT']),
                'BCHARGE': float(ups['BCHARGE']),
                'TONBATT': float(ups['TONBATT']),
                'TIMELEFT': float(ups['TIMELEFT']),
                'NOMPOWER': float(ups['NOMPOWER']),
                'CUMONBATT': float(ups['CUMONBATT']),
                'BATTV': float(ups['BATTV']),
                'OUTPUTV': float(ups['OUTPUTV']),
                'ITEMP': float(ups['ITEMP'])
            },
            'tags': {
                'host': hostname
            }
        }
    ]

    if os.getenv('VERBOSE', 'false').lower() == 'true':
        print(json_body)
        print(client.write_points(json_body))
    else:
        client.write_points(json_body)
    time.sleep(5)
