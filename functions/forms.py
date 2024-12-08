from django import forms


class FunctionUploadForm(forms.Form):
    name = forms.CharField(max_length=100, label="Function Name")
    description = forms.CharField(widget=forms.Textarea, label="Description", required=False)
    function_file = forms.FileField(label="Upload Python Function")
