from django.urls import path, include
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register_user'),
    path('login/', views.user_login, name='user_login'),
    path('profile/', views.get_user_profile, name='get_user_profile'),
    # Household endpoints
    path('households/', views.create_household, name='create_household'),
    path('households/my/', views.get_user_households, name='get_user_households'),
    path('households/<int:household_id>/', views.get_household_detail, name='get_household_detail'),
    path('households/<int:household_id>/update/', views.update_household, name='update_household'),
    path('households/<int:household_id>/join/', views.join_household, name='join_household'),
    path('households/<int:household_id>/leave/', views.leave_household, name='leave_household'),
    path('households/<int:household_id>/members/', views.get_household_members, name='get_household_members'),
]