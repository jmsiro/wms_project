FROM python:3.12-slim

WORKDIR /project

COPY project/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
