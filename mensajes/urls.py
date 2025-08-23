from django.urls import path

from mensajes import views


urlpatterns = [

    path('read/<int:mid>', views.read, name='read'),
    path('send/global', views.send_global, name='send_global'),
    path('send/user/<int:uid>', views.send_user, name='send_user'),
    path('delete/global', views.delete_global, name='delete_global_message'),
    path('test/', views.test_email, name='test_email'),

]