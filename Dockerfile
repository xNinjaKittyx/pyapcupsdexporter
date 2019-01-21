FROM python:2-alpine
MAINTAINER Allan <atribe13@gmail.com>

VOLUME /src/
COPY requirements.txt apcupsd-influxdb-exporter.py /src/
WORKDIR /src
RUN pip install -r requirements.txt

CMD ["python", "-u", "/src/apcupsd-influxdb-exporter.py"]