FROM python

RUN pip install --upgrade pip

RUN pip install kafka-python
RUN pip install python-dateutil

COPY src src