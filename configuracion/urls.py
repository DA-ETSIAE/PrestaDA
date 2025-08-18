from django.urls import path

import configuracion.views
from . import views

urlpatterns = [
    path('', views.settings_page, name='config'),
    path('update/<str:node>/', views.save_config, name='config_update'),
]