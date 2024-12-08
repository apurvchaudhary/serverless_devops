from functions.constants import FUNCTION_FILE_PATH
from django.utils.timezone import now
import subprocess


def save_function_file(function, function_file):

    func_path = f"{FUNCTION_FILE_PATH}/{function.id}_{function_file.name}"

    with open(func_path, 'wb+') as destination:
        for chunk in function_file.chunks():
            destination.write(chunk)

    function.last_deployed = now()
    function.function_file_path = func_path
    function.save()


def run_function_file(function):

    try:
        result = subprocess.run(
            ['python', function.function_file_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        function.status = 'DEPLOYED'
        function.last_deployed = now()
        function.output = result.stdout if result.returncode == 0 else result.stderr
        function.save()
    except subprocess.TimeoutExpired:
        function.status = 'TIMEOUT'
        function.output = "Execution timed out"
        function.save()
    except Exception as e:
        function.status = 'ERROR'
        function.output = str(e)
        function.save()
