"""scholarr URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.core.urls"), name="core"),
    path("api/auth/", include("apps.users.urls"), name="users"),
    path("api/profile/", include("apps.profiles.urls"), name="profiles"),
    path("api/class_group/", include("apps.class_groups.urls"), name="class_groups"),
    path("api/classroom/", include("apps.classrooms.urls"), name="classrooms"),
    path(
        "api/classroom_content/",
        include("apps.classroom_contents.urls"),
        name="classroom_contents",
    ),
    path("api/schedule/", include("apps.schedules.urls"), name="schedule"),
]
