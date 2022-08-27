from django.urls import path

from apps.classroom_contents.api.views import (
    ClassroomClassworkViewSet,
    ClassroomContentView,
    ClassroomResourceViewSet,
    ClassworkSubmissionViewSet,
)

classroom_content_urls = [  # Classroom content CRUD
    path(
        "classroom_id=<int:classroom_id>/list",
        ClassroomContentView.as_view(),
        name="list-classroom-contents",
    ),  # list all classroom contents
]

classwork_urls = [
    #
    ## Classwork
    path(
        "classroom_id=<int:classroom_id>/classwork/list",
        ClassroomClassworkViewSet.as_view({"get": "list_classworks"}),
        name="list-classwork",
    ),  # list
    path(
        "classroom_id=<int:classroom_id>/classwork/create",
        ClassroomClassworkViewSet.as_view({"post": "create"}),
        name="create-classwork",
    ),  # create
    path(
        "classwork/id=<int:classwork_id>/detail",
        ClassroomClassworkViewSet.as_view({"get": "read"}),
        name="detail-classwork",
    ),  # read details
    path(
        "classwork/id=<int:classwork_id>/update",
        ClassroomClassworkViewSet.as_view({"put": "update", "patch": "update"}),
        name="update-classwork",
    ),  # update
    path(
        "classwork/id=<int:classwork_id>/delete",
        ClassroomClassworkViewSet.as_view({"delete": "delete"}),
        name="delete-classwork",
    ),  # delete
]
resource_urls = [
    #
    # ## Resource
    path(
        "classroom_id=<int:classroom_id>/resource/list",
        ClassroomResourceViewSet.as_view({"get": "list_resources"}),
        name="list-resource",
    ),  # list
    path(
        "classroom_id=<int:classroom_id>/resource/create",
        ClassroomResourceViewSet.as_view({"post": "create"}),
        name="create-resource",
    ),  # create
    path(
        "resource/id=<int:resource_id>/detail",
        ClassroomResourceViewSet.as_view({"get": "read"}),
        name="detail-resource",
    ),  # read details
    path(
        "resource/id=<int:resource_id>/update",
        ClassroomResourceViewSet.as_view({"put": "update", "patch": "update"}),
        name="update-resource",
    ),  # update
    path(
        "resource/id=<int:resource_id>/delete",
        ClassroomResourceViewSet.as_view({"delete": "delete"}),
        name="delete-resource",
    ),  # delete
]

submission_urls = [
    #
    ## Submissions
    path(
        "classwork_id=<int:classwork_id>/submission/self/list",
        ClassworkSubmissionViewSet.as_view({"get": "list_self_submissions"}),
        name="list-submission",
    ),  # list
    path(
        "classwork_id=<int:classwork_id>/submission/list",
        ClassworkSubmissionViewSet.as_view({"get": "list_submissions"}),
        name="list-submission",
    ),  # list
    path(
        "classwork_id=<int:classwork_id>/submission/create",
        ClassworkSubmissionViewSet.as_view({"post": "create"}),
        name="create-submission",
    ),  # create
    path(
        "submission/id=<int:submission_id>/detail",
        ClassworkSubmissionViewSet.as_view({"get": "read"}),
        name="detail-submission",
    ),  # read details
    path(
        "submission/id=<int:submission_id>/grade",
        ClassworkSubmissionViewSet.as_view({"put": "update", "patch": "update"}),
        name="grade-submission",
    ),  # grade
    path(
        "submission/id=<int:submission_id>/update",
        ClassworkSubmissionViewSet.as_view({"put": "update", "patch": "update"}),
        name="update-submission",
    ),  # update
    path(
        "submission/id=<int:submission_id>/delete",
        ClassworkSubmissionViewSet.as_view({"delete": "delete"}),
        name="delete-classwork",
    ),  # delete
]

urlpatterns = classroom_content_urls + classwork_urls + resource_urls + submission_urls
