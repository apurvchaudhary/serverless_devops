from django.urls import path
from functions import views


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('upload/', views.upload_function, name='upload_function'),
    path('deploy/<int:function_id>/', views.deploy_function, name='deploy_function'),
]
