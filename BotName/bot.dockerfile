FROM python:3.10

ENV PYTHONUNBUFFERED=1

LABEL version = '0.5'
LABEL master = 'Neveric'

RUN mkdir /NameBot
WORKDIR /NameBot

COPY ./requirements.txt /tmp/

RUN pip3 install --upgrade pip
RUN pip3 install -r /tmp/requirements.txt

COPY . /NameBot/


CMD ["python3", "main.py"]