"""
URL configuration for iq project.
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('login/', auth_views.LoginView.as_view(template_name="main/login.html"), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]

# ──────────────────────────────────────────────────────────────
# ВАЖНО: раздаём статику и медиа ВСЕГДА на локальной разработке
# (чтобы работало и с DEBUG=False — для красивых 404/500)
# ──────────────────────────────────────────────────────────────
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Если у тебя статика лежит в проекте (папка static в корне), а не собрана в STATIC_ROOT:
# используем эту строку вместо предыдущей (закомментируй одну из двух):
# urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])