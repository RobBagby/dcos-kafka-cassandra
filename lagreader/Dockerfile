FROM rbagby/demo_base

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY src src

CMD [ "python", "-u", "src/lagreader.py" ]