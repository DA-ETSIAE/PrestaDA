from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.login_page, name="login"),
    path('local/', views.local_login, name="local"),
    path('users/', views.users, name="users"),
    path('users/profile/<int:pid>/', views.profile_id, name="profile"),
    path('users/profile/', views.profile, name="profile_self"),
    path('setup/', views.setup, name="setup"),
    path('ban/<int:pid>/', views.ban, name="ban"),
    path('banned/', views.banned, name="banned"),
    path('staff/switch', views.make_staff, name="make_staff"),
]