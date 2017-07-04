FROM python

RUN pip install --upgrade pip

RUN pip install kafka-python
RUN pip install python-dateutil
RUN pip install cassandra-driver

COPY src src