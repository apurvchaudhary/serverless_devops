FUNCTION_FILE_PATH = "media/functions"

DOCKER_IMAGE_BUILDER = """FROM python:{runtime}
RUN apt-get update && apt-get install -y netcat-openbsd && apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . /app/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
ENV PYTHONUNBUFFERED=1
RUN chmod +x {entrypoint}
ENTRYPOINT ["python", "{entrypoint}"]
"""
