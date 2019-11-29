FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

RUN pip install pipenv

COPY Pipfile /app/Pipfile
COPY Pipfile.lock /app/Pipfile.lock

RUN pipenv install --system --deploy --ignore-pipfile

COPY /app /app/app
COPY ["main.py", "settings.py", "/app/"] 

ENV VARIABLE_NAME=app
ENV MODULE_NAME=main
