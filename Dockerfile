FROM python:alpine
RUN apk add tzdata
MAINTAINER Daniel A <xNinjaKittyx@users.noreply.github.com>

WORKDIR /src
COPY pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir poetry
RUN poetry install
COPY pyapcupsexporter/ pyapcupsexporter/

CMD ["poetry", "run", "python", "/src/pyapcupsexporter/main.py"]
