FROM python:3.10 as builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc \
    libpq-dev
# graphviz
# ffmpeg

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

FROM python:3.10-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY --from=builder /opt/venv /opt/venv
COPY . /app
WORKDIR /app/src

ENV PATH="/opt/venv/bin:$PATH"
EXPOSE 8081
# ENTRYPOINT ["/opt/venv/bin/python"]
# CMD ["src/api.py"]
# RUN python -c "import nltk; nltk.download('wordnet')"
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8081"]