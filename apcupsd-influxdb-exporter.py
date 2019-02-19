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
host = os.getenv('INFLUXDB_HOST')
apcupsdHost = os.getenv('APCUPSD_HOST', host)

delay = os.getenv('DELAY', 10)
verbose = os.getenv('VERBOSE', 'false').lower() is 'false'


removeTheseKeys = ['DATE', 'STARTTIME', 'END APC']
tagKeys = ['APC', 'HOSTNAME', 'UPSNAME', 'VERSION', 'CABLE',  'MODEL', 'UPSMODE', 'DRIVER', 'APCMODEL', 'END APC']

wattsKey = 'WATTS'
nominalPowerKey = 'NOMPOWER'

client = InfluxDBClient(host, port, user, password, dbname)
client.create_database(dbname)

while True:
    try:
        ups = apc.parse(apc.get(host=apcupsdHost), strip_units=True)
        for key in removeTheseKeys:
            del ups[key]

        tags = {'host': hostname}

        for key in tagKeys:
            if key in ups:
                tags[key] = ups[key]
                del ups[key]

        if wattsKey not in os.environ and nominalPowerKey not in ups:
            raise ValueError("Your UPS does not specify NOMPOWER, you must specify the max watts your UPS can produce.")
        else:
            ups[nominalPowerKey] = os.getenv(wattsKey)

        ups[wattsKey] = float(ups[nominalPowerKey]) * 0.01 * float(ups['LOADPCT'])

        json_body = [
            {
                'measurement': 'apcaccess_status',
                'fields': ups,
                'tags': tags
            }
        ]
        if verbose:
            print(json_body)
            print(client.write_points(json_body))
        else:
            client.write_points(json_body)

        time.sleep(delay)
    except ValueError as valueError:
        raise valueError
    except Exception as e:
        print(e)
