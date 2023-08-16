FROM python:3.8-slim

RUN apt-get update -y
RUN pip install --upgrade pip

RUN mkdir /app
COPY . /app

WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

CMD ["flask", "--app", "webGHT", "run"]