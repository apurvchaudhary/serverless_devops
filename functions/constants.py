FUNCTION_FILE_PATH = "media/functions"

DOCKER_IMAGE_BUILDER = """FROM python:{runtime}
RUN apt-get update && apt-get install -y netcat-openbsd && apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . /app/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
ENV PYTHONUNBUFFERED=1
CMD ["python", "{entrypoint}"]
"""

KUBE_JOB = """apiVersion: batch/v1
kind: Job
metadata:
  name: {name}-{id}
  namespace: serverless
  labels:
    app: {name}-{id}
spec:
  template:
    metadata:
      labels:
        app: {name}-{id}
    spec:
      containers:
      - name: {name}-{id}
        image: {docker_image}
      restartPolicy: Never
  backoffLimit: 3
"""
