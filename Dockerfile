FROM python:3.11-slim
ENV PYTHONUNBUFFERED True

WORKDIR /vid-orca
COPY . .

RUN apt-get update && apt-get install -y gcc cmake build-essential
RUN pip install -r requirements.txt

WORKDIR /vid-orca/src
CMD exec uvicorn main:app --host 0.0.0.0 --port 8080 --workers 1