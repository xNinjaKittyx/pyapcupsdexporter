#!/usr/bin/python
import logging
import os
import time

from apcaccess import status as apc

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

logger = logging.getLogger()
formatter = logging.Formatter("%(asctime)s::%(levelname)s:%(module)s:%(lineno)d - %(message)s")
sh = logging.StreamHandler()
sh.setFormatter(formatter)
logger.addHandler(sh)

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


INFLUX_TOKEN = os.getenv('INFLUX_TOKEN')
INFLUX_URL = os.getenv('INFLUX_URL', "http://localhost:8086")
INFLUX_BUCKET = os.getenv('INFLUX_BUCKET', 'apcupsd')
INFLUX_ORG = os.getenv('INFLUX_ORG')

APCUPSD_HOST = os.getenv('APCUPSD_HOST')

INTERVAL = int(os.getenv('INTERVAL', 10))

print_to_console = os.getenv('VERBOSE', 'false').lower() == 'true'

remove_these_keys = ['DATE', 'STARTTIME', 'END APC','ALARMDEL']
tag_keys = ['APC', 'HOSTNAME', 'UPSNAME', 'VERSION', 'CABLE', 'MODEL', 'UPSMODE', 'DRIVER', 'APCMODEL']

watts_key = 'WATTS'
nominal_power_key = 'NOMPOWER'



def main():
    with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG) as client:
        while True:
            try:
                buckets_api = client.buckets_api()
                bucket = buckets_api.find_bucket_by_name(INFLUX_BUCKET)
                if not bucket:
                    bucket = buckets_api.create_bucket(bucket_name=INFLUX_BUCKET)

            except Exception:
                logger.exception(f"Failed to find or create bucket {INFLUX_BUCKET}")
                time.sleep(INTERVAL)
                continue

            # Grab the UPS Data.
            try:
                ups = apc.parse(apc.get(host=APCUPSD_HOST), strip_units=True)

                remove_irrelevant_data(ups, remove_these_keys)

                tags = {'host': os.getenv('HOSTNAME', ups.get('HOSTNAME', 'apcupsd-influxdb-exporter'))}
                move_tag_values_to_tag_dictionary(ups, tags, tag_keys)

                convert_numerical_values_to_floats(ups)

                if watts_key not in os.environ and nominal_power_key not in ups:
                    raise ValueError(
                        "Your UPS does not specify NOMPOWER, "
                        "you must specify the max watts your UPS can produce."
                    )

                ups[watts_key] = float(os.getenv('WATTS', ups.get('NOMPOWER'))) * 0.01 * float(ups.get('LOADPCT', 0.0))


            except Exception as e:
                logger.exception(f"Failed to parse the UPS data: {e}")
                time.sleep(INTERVAL)
                continue

            try:
                json_body = {
                    'measurement': 'apcaccess_status',
                    'fields': ups,
                    'tags': tags
                }

                if print_to_console:
                    print(json_body)

                write_api = client.write_api(write_options=SYNCHRONOUS)
                write_api.write(INFLUX_BUCKET, record=json_body)
            except Exception as e:
                logger.exception(f"Failed to upload data to InfluxDB: {e}")


            time.sleep(INTERVAL)
            continue

if __name__ == "__main__":
    # Check to make sure all variables are declared
    for var in (INFLUX_TOKEN, INFLUX_URL, INFLUX_BUCKET, INFLUX_ORG, APCUPSD_HOST):
        if not var:
            raise Exception(f"""{f"{var=}".partition('=')[0]} is not defined.""")
    while True:
        try:
            main()
        except Exception as e:
            logger.exception(f"Main loop failed with the following exception: {e}")
