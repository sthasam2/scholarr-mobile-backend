from configs.definitions import DEBUG
from django.urls import path, re_path, include

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework import permissions

from .api.views import HomeView

# if DEBUG:
# schema_view = get_schema_view(
#     openapi.Info(
#         title="Snippets API",
#         default_version="v1",
#         description="Test description",
#         terms_of_service="https://www.google.com/policies/terms/",
#         contact=openapi.Contact(email="contact@snippets.local"),
#         license=openapi.License(name="BSD License"),
#     ),
#     public=True,
#     permission_classes=[permissions.AllowAny],
# )


urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    #
    # DRF_SPECTACULAR Docs
    #
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    # Optional UI:
    path(
        "docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "docs/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
