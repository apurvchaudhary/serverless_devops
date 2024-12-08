from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from functions.forms import FunctionUploadForm
from functions.models import ServerlessFunction
from functions.utils import save_function_file, run_function_file


@require_http_methods(["GET", ])
def dashboard(request):
    functions = ServerlessFunction.objects.all()
    return render(request, 'dashboard.html', {'functions': functions})


@require_http_methods(["GET", "POST"])
def upload_function(request):
    if request.method == 'POST':
        form = FunctionUploadForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            function_file = request.FILES['function_file']
            function = ServerlessFunction.objects.create(
                name=name,
                description=description,
                status='PENDING'
            )
            save_function_file(function, function_file)
            return redirect('dashboard')
    else:
        form = FunctionUploadForm()
    return render(request, 'upload.html', {'form': form})


@require_http_methods(["GET", "POST"])
def deploy_function(request, function_id):
    function = ServerlessFunction.objects.get(id=function_id)
    run_function_file(function)
    return redirect('dashboard')
