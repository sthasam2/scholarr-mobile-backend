from django.urls import path

from apps.class_groups.api.views import ClassGroupViewset

urlpatterns = [
    # Classgroup CRUD
    path(
        "create/",
        ClassGroupViewset.as_view({"post": "post"}),
        name="create class group",
    ),  # create
    path(
        "list/", ClassGroupViewset.as_view({"get": "list"}), name="list class groups"
    ),  # read
    path(
        "id=<int:class_group_id>",
        ClassGroupViewset.as_view({"get": "retrieve"}),
        name="class group detail",
    ),  # read details
    path(
        "id=<int:class_group_id>/update",
        ClassGroupViewset.as_view({"put": "update", "patch": "partial_update"}),
        name="update class group",
    ),  # update
    path(
        "id=<int:class_group_id>/delete",
        ClassGroupViewset.as_view({"delete": "destroy"}),
        name="delete class group",
    ),  # delete
    path(
        "id=<int:class_group_id>/change_active",
        ClassGroupViewset.as_view({"patch": "set_active_inactive"}),
        name="set unset class group active",
    ),  # active/inactive
    #     # Members CRUD
    #     path(),  # invite member
    #     path(),  # request membership
    #     path(),  # accept membership
    #     path(),  # delete membership
]
