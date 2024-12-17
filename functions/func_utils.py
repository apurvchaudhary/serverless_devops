import subprocess
from pathlib import Path

from django.utils.timezone import now

from functions.constants import FUNCTION_FILE_PATH
from functions.docker_utils import DockerBuild


def save_function_file(function, func_file, rq_file=None, entry_file=None):
    func_path = f"{FUNCTION_FILE_PATH}/{function.name}_{function.id}"
    Path(func_path).mkdir(exist_ok=True)
    with open(f"{func_path}/{func_file.name}", "wb+") as destination:
        for chunk in func_file.chunks():
            destination.write(chunk)
    if rq_file:
        with open(f"{func_path}/requirements.txt", "wb+") as destination:
            for chunk in rq_file.chunks():
                destination.write(chunk)
    else:
        with open(f"{func_path}/requirements.txt", "wb+"):
            pass
    if entry_file:
        with open(f"{func_path}/{entry_file.name}", "wb+") as destination:
            for chunk in entry_file.chunks():
                destination.write(chunk)
        function.entrypoint = entry_file.name
    else:
        function.entrypoint = func_file.name
    function.last_deployed = now()
    function.function_path = func_path
    function.save()
    docker = DockerBuild(function)
    docker.build()


def run_function_file(function):
    try:
        result = subprocess.run(
            ["python", function.function_file_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        function.last_deployed = now()
        function.status = "DEPLOYED" if result.returncode == 0 else "ERROR"
        function.output = result.stdout if result.returncode == 0 else result.stderr
        function.save()
    except subprocess.TimeoutExpired:
        function.status = "TIMEOUT"
        function.output = "Execution timed out"
        function.save()
    except Exception as e:
        function.status = "ERROR"
        function.output = str(e)
        function.save()
