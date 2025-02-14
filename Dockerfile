FROM python:3.12-alpine
RUN apk add tzdata
LABEL org.opencontainers.image.authors="xNinjaKittyx@users.noreply.github.com"

WORKDIR /src
RUN pip install --no-cache-dir poetry
COPY pyproject.toml poetry.lock README.md ./
COPY pyapcupsexporter/ pyapcupsexporter/
RUN poetry install --no-root

CMD ["poetry", "run", "python", "/src/pyapcupsexporter/main.py"]
