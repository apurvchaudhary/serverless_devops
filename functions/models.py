from django.db import models


class TimeStamp(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


class ServerlessFunction(TimeStamp):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    last_deployed = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=[
        ('DEPLOYED', 'Deployed'),
        ('FAILED', 'Failed'),
        ('PENDING', 'Pending')
    ], default='PENDING')

    objects = models.Manager()

    def __str__(self):
        return self.name
