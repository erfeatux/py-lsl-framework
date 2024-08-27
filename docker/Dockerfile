FROM python:3.12 AS builder

ENV POETRY_HOME "/opt/poetry" 
ENV PYSETUP_PATH "/opt/pysetup"
ENV VENV_PATH "/opt/pysetup/.venv"
ENV POETRY_VIRTUALENVS_IN_PROJECT true
ENV PYTHONUNBUFFERED 1
WORKDIR $PYSETUP_PATH
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

COPY pyproject.toml ./

RUN pip install --no-cache-dir --upgrade poetry
RUN poetry update
RUN poetry add gunicorn
WORKDIR /app

FROM python:3.12-slim
WORKDIR /app
COPY lslframework/ /app/lslframework/
COPY tests/fakes/ /app/tests/fakes/
COPY main.py /app/
COPY .env /app/
COPY .redis.env /app/
COPY docker/do_install.py do_install.py
COPY --from=builder /opt/pysetup/.venv/ /opt/pysetup/.venv
ARG runtime
ENV PATH="/opt/pysetup/.venv/bin:$PATH"
RUN python do_install.py
RUN rm do_install.py

CMD ["gunicorn", "--worker-class", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8080", "main:app"]
