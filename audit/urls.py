from django.urls import path

from audit import views

urlpatterns = [
    path('', views.logs, name='logs'),
]