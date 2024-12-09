from django.urls import path

from functions import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("upload/", views.upload_function, name="upload_function"),
    path("deploy/<int:function_id>/", views.deploy_function, name="deploy_function"),
    path("output/<int:function_id>/", views.output_function, name="output_function"),
    path("build-logs/<int:function_id>/", views.function_build_logs, name="function_build_logs"),
]
