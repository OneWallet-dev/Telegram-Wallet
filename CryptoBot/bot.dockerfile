FROM python:3.11

ENV PYTHONUNBUFFERED=1

LABEL version = '0.6'
LABEL master = 'BotShackTeam'

RUN mkdir /CryptoBot
WORKDIR /CryptoBot

COPY ./requirements.txt /tmp/

RUN pip3 install --upgrade pip
RUN pip3 install -r /tmp/requirements.txt

COPY . /CryptoBot/
RUN pip3 install --upgrade pip


CMD ./starter.sh