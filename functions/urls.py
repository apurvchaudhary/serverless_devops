from django.urls import path

from functions import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("upload/", views.upload_function, name="upload_function"),
    path("deploy/<int:function_id>/", views.deploy_function, name="deploy_function"),
    path("output/<int:function_id>/", views.output_function, name="output_function"),
    path(
        "build-logs/<int:function_id>/",
        views.function_build_logs,
        name="function_build_logs",
    ),
    path("run/<int:function_id>/", views.run_function, name="run_function"),
    path("remove-orphans/", views.remove_orphans, name="remove_orphans"),
    path(
        "pod-logs/<int:function_id>/<int:stream>/", views.pod_logs_view, name="pod_logs"
    ),
]
