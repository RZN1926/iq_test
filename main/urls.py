from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('test/', views.iq_test_view, name='iq_test'),   # <-- Новый маршрут
    path('result/', views.test_result, name='test_result'),  # <-- Показывает результат
    path('profile/', views.profile, name='profile'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('register/', views.register, name='register'),
    path('profile/delete/', views.delete_profile, name='delete_profile'),
]
