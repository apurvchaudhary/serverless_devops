from venv import create

from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from functions.forms import FunctionUploadForm
from functions.models import ServerlessFunction
from functions.func_utils import save_function_file, run_function_file
from functions.docker_utils import DockerBuild


@require_http_methods(
    [
        "GET",
    ]
)
def dashboard(request):
    functions = ServerlessFunction.objects.all()
    return render(request, "dashboard.html", {"functions": functions})


@require_http_methods(["GET", "POST"])
def upload_function(request):
    if request.method == "POST":
        form = FunctionUploadForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data["name"]
            description = form.cleaned_data["description"]
            runtime = form.cleaned_data["runtime"]
            version = form.cleaned_data["version"]
            function_file = request.FILES["function_file"]
            rq_file = request.FILES.get("rq_file")
            entrypoint = request.FILES.get("entrypoint")
            function = ServerlessFunction.objects.create(
                name=name, description=description, status="PENDING", runtime=runtime, version=version
            )
            save_function_file(function, function_file, rq_file, entrypoint)
            return redirect("dashboard")
    else:
        form = FunctionUploadForm()
    return render(request, "upload.html", {"form": form})


@require_http_methods(["GET"])
def deploy_function(request, function_id):
    function = ServerlessFunction.objects.get(id=function_id)
    docker = DockerBuild(function)
    docker.build()
    return redirect("dashboard")


@require_http_methods(["GET"])
def output_function(request, function_id):
    function = ServerlessFunction.objects.get(id=function_id)
    return render(request, "function_output.html", {"function": function})


@require_http_methods(["GET"])
def function_build_logs(request, function_id):
    function = ServerlessFunction.objects.get(id=function_id)
    context = {"function": function}
    try:
        with open(f"{function.function_path}/build.log", "r") as logs:
            context["logs"] = logs.read()
    except FileNotFoundError:
        pass
    return render(request, "function_output.html", context)
