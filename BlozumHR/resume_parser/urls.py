"""resume_parser URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path, include
from parser_app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("postsignIn/", views.postsignIn, name="postsignIn"),
    path("", views.signIn),
    path("homepage/", views.homepage, name="homepage"),
    path("jd_form/", views.jd_form, name="jd_form"),
    path("tanmayjuneja801/", views.signUp, name="signup"),
    path("logout/", views.logout, name="log"),
    path("postsignUp/", views.postsignUp),
    path("ats_import/", views.import_from_ATS, name="import_from_ATS"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
