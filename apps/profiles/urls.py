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
        "detail/user=<slug:username>",
        ProfileDetailView.as_view(),
        name="profile-detail",
    ),
    path(
        "summary/user=<slug:username>",
        ProfileSummaryView.as_view(),
        name="profile-summary",
    ),
    path(
        "update/user=<slug:username>",
        UpdateProfileView.as_view(),
        name="update-profile",
    ),
    path(
        "enable_disable_persona/user=<slug:username>",
        EnableDisablePersonaView.as_view(),
        name="update-profile-use-persona",
    ),
    path(
        "set_persona/user=<slug:username>",
        SetPersonaView.as_view(),
        name="update-profile-use-persona",
    ),
    path(
        "change_private/user=<slug:username>",
        ChangePrivateProfileView.as_view(),
        name="update-profile",
    ),
    path(
        "upload_images/user=<slug:username>",
        ProfileImageUploadView.as_view(),
        name="update-profile",
    ),
]
