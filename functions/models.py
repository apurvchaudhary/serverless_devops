from django.db import models


class TimeStamp(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


class ServerlessFunction(TimeStamp):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, default="PENDING")
    last_deployed = models.DateTimeField(null=True, blank=True)
    function_path = models.CharField(max_length=200)
    output = models.TextField(blank=True, null=True)
    entrypoint = models.CharField(max_length=100, null=True)
    runtime = models.CharField(max_length=100)
    version = models.CharField(max_length=100)
    image = models.CharField(max_length=250, null=True)

    objects = models.Manager()

    def __str__(self):
        return self.name
