from docker import from_env
from docker.errors import BuildError, APIError

from functions.constants import DOCKER_IMAGE_BUILDER
from functions.models import ServerlessFunction
from os import remove
from glob import glob


class DockerBuild:

    def __init__(self, function: ServerlessFunction):
        self.function = function
        self.name = function.name
        self.version = function.version
        self.path = function.function_path
        self.CONTEXT = {
            "path": self.path,
            "entrypoint": function.entrypoint,
            "name": self.name,
            "runtime": function.runtime,
            "version": self.version,
        }

    def create(self):
        with open(f"{self.path}/Dockerfile", "a+") as dockerfile:
            dockerfile.write(DOCKER_IMAGE_BUILDER.format(**self.CONTEXT))
        self.function.status = "INITIALISED"
        self.function.save()

    def copy_logs(self, logs):
        files = glob(f"{self.path}/*")
        for f in files:
            remove(f)
        with open(f"{self.path}/build.log", "w+") as content:
            for log in logs:
                if "stream" in log:
                    content.write(log["stream"])

    def build(self):
        client = from_env()
        try:
            image, build_logs = client.images.build(path=self.path, tag=f"{self.name}:{self.version}", rm=True)
            self.function.status = "DEPLOYED"
            self.function.image = f"{image}"
            self.copy_logs(build_logs)
        except (BuildError, APIError) as e:
            self.function.status = "FAILED"
            self.function.output = str(e)
        finally:
            self.function.save()
