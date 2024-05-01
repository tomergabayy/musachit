FROM python:3.11-slim-bookworm
WORKDIR /app
RUN pip install flask gunicorn requests flask_sqlalchemy pymysql cryptography flask_login flask_wtf wtforms boto3 botocore
COPY ./ .
CMD gunicorn -w 2 -b 0.0.0.0:8000 app:app