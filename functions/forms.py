from django import forms


class FunctionUploadForm(forms.Form):
    name = forms.CharField(max_length=100, label="Function Name")
    runtime = forms.CharField(max_length=100, label="Environment Runtime eg. 3.8-slim")
    version = forms.CharField(max_length=100, label="Function Version eg. 1.0")
    description = forms.CharField(widget=forms.Textarea, label="Description", required=False)
    function_file = forms.FileField(label="Upload Python Function")
    rq_file = forms.FileField(label="Upload requirements", required=False)
    entrypoint = forms.FileField(label="Upload entrypoint", required=False)
