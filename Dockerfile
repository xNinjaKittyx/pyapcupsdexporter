FROM python:2-alpine
MAINTAINER Allan <atribe13@gmail.com>

WORKDIR /src
COPY requirements.txt apcupsd-influxdb-exporter.py /src/
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "/src/apcupsd-influxdb-exporter.py"]