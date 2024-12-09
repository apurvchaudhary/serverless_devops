from glob import glob
from os import remove

from docker import from_env
from docker.errors import BuildError, APIError

from functions.constants import DOCKER_IMAGE_BUILDER
from functions.models import ServerlessFunction


class DockerBuild:
    CLIENT = from_env()
    REGISTRY_USER = "apurvchaudhary"

    def __init__(self, function: ServerlessFunction):
        self.function = function
        self.name = function.name
        self.version = function.version
        self.path = function.function_path
        self.full_tag = f"{self.REGISTRY_USER}/{self.name}:{self.version}"
        self.CONTEXT = {
            "path": self.path,
            "entrypoint": function.entrypoint,
            "name": self.name,
            "runtime": function.runtime,
            "version": self.version,
        }

    def __remove_tmp(self):
        files = glob(f"{self.path}/*")
        for f in files:
            remove(f)

    def __write_logs(self, logs, build=False, push=False):
        if build:
            with open(f"{self.path}/function.log", "w+") as content:
                for log in logs:
                    if "stream" in log:
                        content.write(log["stream"])
        if push:
            with open(f"{self.path}/function.log", "w+") as log_file:
                log_file.write("\n".join(logs))

    def __build(self):
        try:
            image, build_logs = self.CLIENT.images.build(path=self.path, tag=f"{self.name}:{self.version}", rm=True)
            self.function.status = "CREATED"
            self.function.image = f"{image.id}"
            self.__remove_tmp()
            self.__write_logs(build_logs, build=True)
        except (BuildError, APIError) as e:
            self.function.status = "FAILED"
            self.function.output = str(e)
        finally:
            self.function.save()

    def build(self):
        with open(f"{self.path}/Dockerfile", "a+") as dockerfile:
            dockerfile.write(DOCKER_IMAGE_BUILDER.format(**self.CONTEXT))
        self.__build()

    def deploy(self):
        logs = []
        try:
            image = self.CLIENT.images.get(self.function.image)
            image.tag(self.full_tag)
            for log in self.CLIENT.images.push(self.full_tag, stream=True, decode=True):
                logs.append(log.get("status", ""))
            self.__remove_tmp()
            self.__write_logs(logs, push=True)
            self.function.status = "DEPLOYED"
            self.function.output = "Pushed to dockerhub successfully!!!"
            self.CLIENT.images.remove(image.id, force=True)
        except APIError as e:
            self.function.status = "FAILED"
            self.function.output = str(e)
        finally:
            self.function.save()
