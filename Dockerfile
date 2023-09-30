FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_ROOT_USER_ACTION=ignore

WORKDIR /usr/src

COPY  ./requirements.txt /usr/src/requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /usr/src/requirements.txt

COPY . /usr/src
