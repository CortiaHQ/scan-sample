FROM python:3.9-slim

WORKDIR /srv

RUN pip install --no-cache-dir uv==0.12.18

COPY . /srv/api

WORKDIR /srv/api
RUN uv sync --frozen --extra test

ENV PATH="/srv/api/.venv/bin:${PATH}"

WORKDIR /srv

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
