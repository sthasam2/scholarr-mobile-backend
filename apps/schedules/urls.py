from django.urls import path

from apps.schedules.api.views import ScheduleViewset

urlpatterns = [
    path(
        "self/list",
        ScheduleViewset.as_view({"get": "self_list"}),
        name="self-list-classroom-schedule",
    ),  # self list
    path(
        "classroom/id=<int:classroom_id>/list",
        ScheduleViewset.as_view({"get": "list"}),
        name="list-classroom-schedule",
    ),  # list
    path(
        "classroom/id=<int:classroom_id>/create",
        ScheduleViewset.as_view({"post": "create"}),
        name="create-schedule",
    ),  # create
    path(
        "id=<int:schedule_id>/detail",
        ScheduleViewset.as_view({"get": "detail_schedule"}),
        name="detail-schedule",
    ),  # detail
    path(
        "id=<int:schedule_id>/update",
        ScheduleViewset.as_view({"put": "update", "patch": "update"}),
        name="update-schedule",
    ),  # update
    path(
        "id=<int:schedule_id>/delete",
        ScheduleViewset.as_view({"delete": "delete"}),
        name="delete-schedule",
    ),  # delete
]
