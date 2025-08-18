from django.urls import path

from gestor import views

urlpatterns = [
    path('validate/', views.validate, name='validate'),
    path('delete/type', views.delete_type, name='delete_type'),
    path('delete/item', views.delete_item, name='delete_item'),
    path('new/type', views.new_type, name='new_type'),
    path('new/item', views.new_item, name='new_item'),

    path('print/', views.print_list, name='print'),
]