#!/usr/bin/python
import os
import time

from apcaccess import status as apc
from influxdb import InfluxDBClient

dbname = os.getenv('INFLUXDB_DATABASE', 'apcupsd')
user = os.getenv('INFLUXDB_USER')
password = os.getenv('INFLUXDB_PASSWORD')
port = os.getenv('INFLUXDB_PORT', 8086)
host = os.getenv('INFLUXDB_HOST')
apcupsdHost = os.getenv('APCUPSD_HOST', host)

delay = os.getenv('DELAY', 10)

removeTheseKeys = ['DATE', 'STARTTIME', 'END APC']
tagKeys = ['APC', 'HOSTNAME', 'UPSNAME', 'VERSION', 'CABLE', 'MODEL', 'UPSMODE', 'DRIVER', 'APCMODEL', 'END APC']

wattsKey = 'WATTS'
nominalPowerKey = 'NOMPOWER'

client = InfluxDBClient(host, port, user, password, dbname)
client.create_database(dbname)

while True:
    try:
        ups = apc.parse(apc.get(host=apcupsdHost), strip_units=True)
        for key in removeTheseKeys:
            del ups[key]

        tags = {'host': os.getenv('HOSTNAME', ups.get('HOSTNAME', 'apcupsd-influxdb-exporter'))}

        for key in tagKeys:
            if key in ups:
                tags[key] = ups[key]
                del ups[key]

        if wattsKey not in os.environ and nominalPowerKey not in ups:
            raise ValueError("Your UPS does not specify NOMPOWER, you must specify the max watts your UPS can produce.")

        for key in ups:
            if ups[key].replace('.', '', 1).isdigit():
                ups[key] = float(ups[key])

        ups[wattsKey] = float(os.getenv('WATTS', ups.get('NOMPOWER', 0.0))) * 0.01 * float(ups.get('LOADPCT', 0.0))

        json_body = [
            {
                'measurement': 'apcaccess_status',
                'fields': ups,
                'tags': tags
            }
        ]
        if os.getenv('VERBOSE', 'false').lower() == 'true':
            print(json_body)
            print(client.write_points(json_body))
        else:
            client.write_points(json_body)

        time.sleep(delay)
    except ValueError as valueError:
        raise valueError
    except Exception as e:
        print(e)
