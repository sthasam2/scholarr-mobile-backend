from django.urls import path

from apps.classrooms.api.views import ClassroomUserViewSet, ClassroomViewset

classroom_urls = [  ## Classroom CRUD
    path(
        "list", ClassroomViewset.as_view({"get": "list"}), name="list-classroom"
    ),  # list
    path(
        "self/list",
        ClassroomViewset.as_view({"get": "list_self_classrooms"}),
        name="list-self-classroom-list",
    ),  # user list
    path(
        "create", ClassroomViewset.as_view({"post": "create"}), name="classroom-create"
    ),  # create
    path(
        "id=<int:classroom_id>/detail",
        ClassroomViewset.as_view({"get": "retrieve"}),
        name="detail-classroom",
    ),  # read details
    path(
        "id=<int:classroom_id>/update",
        ClassroomViewset.as_view({"put": "update", "patch": "update"}),
        name="update-classroom",
    ),  # update
    path(
        "id=<int:classroom_id>/toggle_archive",
        ClassroomViewset.as_view({"post": "toggle_archive"}),
        name="toggle-archive-classroom",
    ),  # archive/unarchive
    path(
        "id=<int:classroom_id>/delete",
        ClassroomViewset.as_view({"delete": "destroy"}),
        name="delete-classroom",
    ),  # delete
]


classroom_member_urls = [
    #
    ## Invite Request CRUD
    path(
        "invite_request/self/list/<slug:target_type>",
        ClassroomUserViewSet.as_view({"get": "list_invites_requests"}),
        name="list-invite-request",
    ),  # list invite request
    path(
        "invite_request/self/list",
        ClassroomUserViewSet.as_view({"get": "list_invites_requests"}),
        name="list-invite-request",
    ),  # list invite request
    path(
        "id=<int:classroom_id>/invite_request/list",
        ClassroomUserViewSet.as_view({"get": "list_classroom_invites_requests"}),
        name="list-classroom-invite-request",
    ),  # list classroom invite request
    path(
        "id=<int:classroom_id>/member/list",
        ClassroomUserViewSet.as_view({"get": "list_classroom_members"}),
        name="list-classroom-members",
    ),  # list classroom invite request
    path(
        "invite/create",
        ClassroomUserViewSet.as_view({"post": "create_invite"}),
        name="create-invite",
    ),  # create invite
    path(
        "request/create",
        ClassroomUserViewSet.as_view({"post": "create_request"}),
        name="create-request",
    ),  # create request
    path(
        "invite_request/id=<int:invite_request_id>/detail",
        ClassroomUserViewSet.as_view({"get": "detail_invite_request"}),
        name="detail-invite-request",
    ),  # detail invite_request
    # path(
    #     "request/id=<int:request_id>/detail",
    #     ClassroomUserViewSet.as_view({"get": "detail_invite_request"}),
    #     name="detail-request",
    # ),  # detail request
    path(
        "invite_request/id=<int:invite_request_id>/accept",
        ClassroomUserViewSet.as_view({"post": "accept_invite_or_request"}),
        name="accept-invite-request",
    ),  # accept
    path(
        "invite_request/id=<int:invite_request_id>/reject",
        ClassroomUserViewSet.as_view({"post": "reject_invite_or_request"}),
        name="reject-invite-request",
    ),  # reject
    path(
        "invite_request/id=<int:invite_request_id>/delete",
        ClassroomUserViewSet.as_view({"delete": "delete_invite_or_request"}),
        name="delete-invite-request",
    ),  # delete
]

urlpatterns = classroom_urls + classroom_member_urls
