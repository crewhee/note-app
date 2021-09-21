# syntax=docker/dockerfile:1

FROM python:3.9-slim-buster


COPY . .
WORKDIR .

RUN pip install -r requirements.txt

ENV FLASK_APP notes
ENV FLASK_DEBUG 1

RUN flask init-db
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5000"]