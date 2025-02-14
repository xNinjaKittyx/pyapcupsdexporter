# pyapcupsdexporter

Dockerized Python script that will send data from [apcupsd](http://www.apcupsd.org/) to [influxdb](https://hub.docker.com/_/influxdb).

This is a fork of https://github.com/atribe/apcupsd-influxdb-exporter to add InfluxDB 2.x support.

## How to build
Building the image is straight forward:
* Git clone this repo
* `docker build -t pyapcupsdexporter  .`

## Environment Variables
These are all the available environment variables, along with some example values, and a description.

With the changes to InfluxDB 2.0, this currently requires you to have an ORG + Token setup instead of the base username/password.


| Environment Variable | Example Value | Description |
| -------------------- | ------------- | ----------- |
| WATTS |  1000 | if your ups doesn't have NOMPOWER, set this to be the rated max power, if you do have NOMPOWER, don't set this variable |
| APCUPSD_HOST | 192.168.1.100 | host running apcupsd, defaults to the value of influxdb_host |
| INFLUX_URL | http://192.168.1.100:8086 | required. URL to your InfluxDB Instance. |
| INFLUX_ORG | my-org | required, the name of the organization. |
| INFLUX_TOKEN | somebase64string | required, needed to log in to InfluxDB instance |
| INFLUXDB_PORT |  8086 | optional, defaults to 8086 |
| INFLUXDB_PORT |  8086 | optional, defaults to 8086 |
| INTERVAL | 10 | optional, defaults to 10 seconds |
| VERBOSE | true | if anything but true docker logging will show no output |

## How to Use

### Run docker container directly
```bash
docker run --rm  -d --name="pyapcupsdexporter" \
    -e "WATTS=600" \
    -e "INFLUX_URL=http://10.0.1.11:8086" \
    -e "INFLUX_TOKEN=asdflkajwse;orfiajsdklfjaskl==" \
    -e "INFLUX_ORG=my-org" \
    -e "APCUPSD_HOST=10.0.1.11" \
    -t xNinjaKittyx/pyapcupsdexporter
```
Note: if your UPS does not include the NOMPOWER metric, you will need to include the WATTS environment variable in order to compute the live-power consumption
metric.

### Run from docker-compose
```bash
version: '3'
services:
  pyapcupsdexporter:
    image: ghcr.io/xninjakittyx/pyapcupsdexporter:master
    container_name: apcupsd-influxdb-exporter
    restart: always
    environment:
      WATTS: 1500 # if your ups doesn't have NOMPOWER, set this to be the rated max power, if you do have NOMPOWER, don't set this variable
      APCUPSD_HOST: 10.0.1.11  # Host running APCUPSD
      INFLUX_URL: http://10.0.1.11:8086  # URL of the InfluxDB instance
      INFLUX_ORG: my-org  # ORG Associated with your influx bucket.
      INFLUX_TOKEN:  # Token associated with your influx instance/org
      INFLUX_BUCKET: apcupsd
      INTERVAL: 5
      VERBOSE: true
```

If you want to debug the apcaccess output or the send to influxdb, set the environment variable "VERBOSE" to "true"
