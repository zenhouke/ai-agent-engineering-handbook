FROM python:3.13-slim
WORKDIR /workspace
RUN apt-get update && apt-get install -y --no-install-recommends fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --disable-pip-version-check -r requirements.txt
COPY . .
EXPOSE 32140
CMD ["python", "scripts/dev.py"]
