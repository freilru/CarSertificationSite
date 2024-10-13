from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('project/create/', views.create_project, name='create_project'),
    path('project/<int:project_id>', views.project_detail, name='project_detail'),
    path('project/<int:project_id>/requirement/create', views.create_requirement, name='create_requirement'),
    path('project/<int:project_id>/requirement/<int:requirement_id>/delete', views.delete_requirement,
         name='delete_requirement'),
    path('project/<int:project_id>/requirement/<int:requirement_id>/check', views.check_detail, name='check_detail'),
    path('project/<int:project_id>/requirement/<int:requirement_id>/check/delete/<int:check_id>', views.delete_check,
         name='delete_check'),
    path('upload_pdf', views.upload_pdf, name='upload_pdf'),
]
