from django.shortcuts import render, redirect
from functions.models import ServerlessFunction
from django.views.decorators.http import require_http_methods
from functions.forms import FunctionUploadForm
from django.utils.timezone import now


@require_http_methods(["GET",])
def dashboard(request):
    functions = ServerlessFunction.objects.all()
    return render(request, 'dashboard.html', {'functions': functions})


@require_http_methods(["GET", "POST"])
def upload_function(request):
    if request.method == 'POST':
        form = FunctionUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Handle the uploaded file
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            function_file = request.FILES['function_file']

            # Save the file and function metadata in the database
            function = ServerlessFunction.objects.create(
                name=name,
                description=description,
                status='PENDING'
            )

            # Save the function file to the media directory
            with open(f'media/functions/{function.id}_{function_file.name}', 'wb+') as destination:
                for chunk in function_file.chunks():
                    destination.write(chunk)

            function.last_deployed = now()
            function.save()

            return redirect('dashboard')

    else:
        form = FunctionUploadForm()

    return render(request, 'upload.html', {'form': form})
