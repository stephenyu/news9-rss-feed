FROM python:alpine3.16

WORKDIR /usr/src/app

ENV FLASK_APP=app

COPY requirements.txt ./
COPY app.py ./
COPY rfeed.py ./

RUN pip install --no-cache-dir -r requirements.txt

CMD ["flask", "run", "--host=0.0.0.0"]
