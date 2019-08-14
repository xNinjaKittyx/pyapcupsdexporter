#!/usr/bin/python
import os
import time

from apcaccess import status as apc
from influxdb import InfluxDBClient

def remove_irrelevant_data(status, remove_these_keys):
    for key in remove_these_keys:
        status.pop(key, None)

def move_tag_values_to_tag_dictionary(status, tags, tag_keys):
    for key in tag_keys:
        if key in status:
            tags[key] = status[key]
            status.pop(key, None)

def convert_numerical_values_to_floats(ups):
    for key in ups:
        if ups[key].replace('.', '', 1).isdigit():
            ups[key] = float(ups[key])

dbname = os.getenv('INFLUXDB_DATABASE', 'apcupsd')
user = os.getenv('INFLUXDB_USER')
password = os.getenv('INFLUXDB_PASSWORD')
port = os.getenv('INFLUXDB_PORT', 8086)
host = os.getenv('INFLUXDB_HOST')
apcupsd_host = os.getenv('APCUPSD_HOST', host)

delay = os.getenv('INTERVAL', 10)

print_to_console = os.getenv('VERBOSE', 'false').lower() == 'true'

remove_these_keys = ['DATE', 'STARTTIME', 'END APC']
tag_keys = ['APC', 'HOSTNAME', 'UPSNAME', 'VERSION', 'CABLE', 'MODEL', 'UPSMODE', 'DRIVER', 'APCMODEL', 'END APC']

watts_key = 'WATTS'
nominal_power_key = 'NOMPOWER'

client = InfluxDBClient(host, port, user, password, dbname)
client.create_database(dbname)

while True:
    try:
        ups = apc.parse(apc.get(host=apcupsd_host), strip_units=True)

        remove_irrelevant_data(ups, remove_these_keys)

        tags = {'host': os.getenv('HOSTNAME', ups.get('HOSTNAME', 'apcupsd-influxdb-exporter'))}
        move_tag_values_to_tag_dictionary(ups, tags, tag_keys)

        convert_numerical_values_to_floats(ups)

        if watts_key not in os.environ and nominal_power_key not in ups:
            raise ValueError("Your UPS does not specify NOMPOWER, you must specify the max watts your UPS can produce.")

        ups[watts_key] = float(os.getenv('WATTS', ups.get('NOMPOWER'))) * 0.01 * float(ups.get('LOADPCT', 0.0))

        json_body = [
            {
                'measurement': 'apcaccess_status',
                'fields': ups,
                'tags': tags
            }
        ]

        if print_to_console:
            print(json_body)
            print(client.write_points(json_body))
        else:
            client.write_points(json_body)

        time.sleep(delay)
    except ValueError as valueError:
        raise valueError
    except Exception as e:
        print(e)
