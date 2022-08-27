from django.urls import path

from apps.plagiarism_detector.api.views import PlagiarismListView


urlpatterns = [
    path(
        "submission_id=<int:submission_id>/list",
        PlagiarismListView.as_view(),
        name="list-plagiarism",
    ),
]
