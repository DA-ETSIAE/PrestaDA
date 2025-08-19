"""
URL configuracion for prestamos project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from xml.etree.ElementInclude import include

from django.contrib import admin
from django.urls import include, path

from gestor import views as gestor_views
from . import views
import usuarios

urlpatterns = [

    path('', views.index, name="index"),
    path('store/', views.store, name="store"),
    path('reserve/<int:tid>', gestor_views.reserve, name="reserve"),
    path('', include("usuarios.urls")),
    path('config/', include('configuracion.urls')),
    path('manager/', include('gestor.urls')),
    path('msg/', include('mensajes.urls')),
    path('audit/', include('audit.urls')),
    path('print/petition/<int:id>', views.print_profile, name='print_petition'),


    # from .gestor
    path('items/', gestor_views.items, name='items'),
    path('item/<int:iid>', gestor_views.item_profile, name='item'),

    path('types/', gestor_views.types, name='types'),
    path('type/<int:tid>', gestor_views.type_profile, name='type'),

    path('petitions/', gestor_views.petitions, name='petitions'),
    path('petition/<int:pid>/', gestor_views.petition, name='petition'),


    # Misc
    path('oidc/', include('mozilla_django_oidc.urls')),
    path('admin/login/', usuarios.views.login_page),
    path('admin/', admin.site.urls),


]
