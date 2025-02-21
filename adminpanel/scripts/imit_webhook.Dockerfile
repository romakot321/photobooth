FROM python:3.13-slim
EXPOSE 80

WORKDIR /app

COPY ./requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

COPY ./imit_webhook.py ./imit_webhook.py
CMD python3 imit_webhook.py
