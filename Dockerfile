FROM python:3.11.4

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install "poetry==1.5.1"
RUN poetry config virtualenvs.create false --local

COPY diploma-frontend ./diploma-frontend
COPY pyproject.toml ./
COPY poetry.lock ./
RUN poetry update
RUN python ./diploma-frontend/setup.py sdist
RUN pip install ./diploma-frontend/dist/diploma-frontend-0.6.tar.gz

COPY megano .

CMD ["gunicorn", "megano.wsgi:application", "--bind", "0.0.0.0:8000"]