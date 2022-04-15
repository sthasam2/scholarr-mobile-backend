from django.urls import path

from apps.profiles.api.views import (
    ChangePrivateProfileView,
    EnableDisablePersonaView,
    ProfileDetailView,
    ProfileImageUploadView,
    ProfileSummaryView,
    SetPersonaView,
    UpdateProfileView,
)

from .models import Profile

urlpatterns = [
    path(
        "username=<slug:username>/detail",
        ProfileDetailView.as_view(),
        name="profile-detail",
    ),
    path(
        "username=<slug:username>/summary",
        ProfileSummaryView.as_view(),
        name="profile-summary",
    ),
    path(
        "username=<slug:username>/update",
        UpdateProfileView.as_view(),
        name="update-profile",
    ),
    path(
        "username=<slug:username>/enable_disable_persona",
        EnableDisablePersonaView.as_view(),
        name="update-profile-use-persona",
    ),
    path(
        "username=<slug:username>/set_persona",
        SetPersonaView.as_view(),
        name="update-profile-use-persona",
    ),
    path(
        "username=<slug:username>/change_private",
        ChangePrivateProfileView.as_view(),
        name="update-profile",
    ),
    path(
        "username=<slug:username>/upload_images",
        ProfileImageUploadView.as_view(),
        name="update-profile",
    ),
]
