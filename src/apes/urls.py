"""
URL configuration for apes project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from pages.views import (
    landing_view,
    homepage_view,
    guest_login_view,
    logout_view,
    guest_login_view,
)

from session.views import (
    register_view,
    successful_account_creation_view,
    login_view,
)

urlpatterns = [
    path('admin/', admin.site.urls, name="admin_view"),
    path('', landing_view, name="landing_view"),
    path('home/', homepage_view, name="homepage_view"),
    path('register/', register_view, name="register_view"),
    path('register/success/', successful_account_creation_view, name="successful_account_creation"),
    path('login/', login_view, name="login_view"),
    path('guest_home/', guest_login_view, name="guest_login_view"),
    path('logout/', logout_view, name="logout_view"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)