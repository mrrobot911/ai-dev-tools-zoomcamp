from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register_user'),
    path('login/', views.user_login, name='user_login'),
    path('profile/', views.get_user_profile, name='get_user_profile'),
]