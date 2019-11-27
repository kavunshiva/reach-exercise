FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

RUN pip install pipenv

COPY Pipfile /app/Pipfile
COPY Pipfile.lock /app/Pipfile.lock

RUN pipenv install --system --deploy --ignore-pipfile

COPY . /app

ENV VARIABLE_NAME=app
ENV MODULE_NAME=main
