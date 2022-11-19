FROM python:3.11

ENV PYTHONUNBUFFERED=1

LABEL version = '0.5'
LABEL master = 'Neveric'

RUN mkdir /CryptoBot
WORKDIR /CryptoBot

COPY ./requirements.txt /tmp/

RUN pip3 install --upgrade pip
RUN pip3 install -r /tmp/requirements.txt

COPY . /CryptoBot/


CMD ["python3", "main.py"]