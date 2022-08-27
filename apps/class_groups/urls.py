from django.urls import path

from apps.class_groups.api.views import ClassGroupMemberViewset, ClassGroupViewset

classgroup_urls = [
    # Classgroup CRUD
    path(
        "create",
        ClassGroupViewset.as_view({"post": "post"}),
        name="create-class-group",
    ),  # create
    path(
        "list", ClassGroupViewset.as_view({"get": "list"}), name="list-class-groups"
    ),  # read
    path(
        "self/list",
        ClassGroupViewset.as_view({"get": "list_self_classgroups"}),
        name="list-self-class-groups",
    ),  # read list for user
    path(
        "id=<int:class_group_id>/detail",
        ClassGroupViewset.as_view({"get": "retrieve"}),
        name="detail-class-group",
    ),  # read details
    path(
        "id=<int:class_group_id>/update",
        ClassGroupViewset.as_view({"put": "update", "patch": "partial_update"}),
        name="update-class-group",
    ),  # update
    path(
        "id=<int:class_group_id>/delete",
        ClassGroupViewset.as_view({"delete": "destroy"}),
        name="delete-class-group",
    ),  # delete
    path(
        "id=<int:class_group_id>/toggle_active",
        ClassGroupViewset.as_view({"patch": "toggle_active"}),
        name="toggle-class-group-active",
    ),  # active/inactive
]

classgroup_member_uls = [
    # Members CRUD
    path(
        "invite/create",
        ClassGroupMemberViewset.as_view({"post": "create_invite"}),
        name="invite-classgroup-member",
    ),  # invite member via id, username, email to classgroup via id, code
    path(
        "request/create",
        ClassGroupMemberViewset.as_view({"post": "create_request"}),
        name="request-classgroup-membership",
    ),  # request membership via id, code
    path(
        "invite_request/id=<int:invite_request_id>/accept",
        ClassGroupMemberViewset.as_view({"post": "accept_invite_or_request"}),
        name="accept-invite-or-request",
    ),  # accept membership
    path(
        "invite_request/id=<int:invite_request_id>/reject",
        ClassGroupMemberViewset.as_view({"post": "reject_invite_or_request"}),
        name="reject-invite-or-request",
    ),  # reject membership
    path(
        "invite_request/id=<int:invite_request_id>/delete",
        ClassGroupMemberViewset.as_view({"delete": "delete_invite_or_request"}),
        name="delete-invite-or-request",
    ),  # delete membership
    path(
        "invite_request/self/list",
        ClassGroupMemberViewset.as_view({"get": "list_invites_requests"}),
        name="delete-invite-or-request",
    ),  # list membership
    path(
        "id=<int:classgroup_id>/invite_request/list",
        ClassGroupMemberViewset.as_view({"get": "list_classgroup_invites_requests"}),
        name="delete-invite-or-request",
    ),  # list membership
    path(
        "id=<int:classgroup_id>/member/list",
        ClassGroupMemberViewset.as_view({"get": "list_classgroup_members"}),
        name="delete-invite-or-request",
    ),  # list membership
]

urlpatterns = classgroup_urls + classgroup_member_uls
