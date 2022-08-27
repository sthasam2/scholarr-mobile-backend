from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.classroom_contents.api.serializers import *
from apps.classroom_contents.models import (
    Classwork,
    ClassworkHasAttachment,
    ClassworkHasSubmission,
    Resource,
    ResourceHasAttachment,
    Submission,
    SubmissionHasAttachment,
)
from apps.classroom_contents.permissions import (
    IsSubmissionOwner,
    IsSubmissionOwnerOrClassroomOwnerOrTeacher,
)
from apps.classroom_contents.utils import (
    check_and_handle_attachments,
    get_url_id_classwork_or_raise,
    get_url_id_resource_or_raise,
    get_url_id_submission_or_raise,
)
from apps.classrooms.models import ClassroomHasClasswork, ClassroomHasResource
from apps.classrooms.permissions import IsClassroomMember, IsClassroomOwnerOrTeacher
from apps.classrooms.utils import get_url_id_classroom_or_raise
from apps.core.decorators import try_except_http_error_decorator
from apps.core.helpers import RequestFieldsChecker, create_200
from apps.core.permissions import IsAuthenticatedCustom
from apps.classrooms.api.serializers import ClassroomOnlySerializer


class ClassroomContentView(APIView):

    classwork_serializer_class = ReadClassworkSerializer
    resource_serializer_class = ReadResourceSerializer

    @try_except_http_error_decorator
    def get(self, request, *args, **kwargs):
        """ """

        classroom_id = kwargs.get("classroom_id", None)

        if classroom_id:
            classroom_instance = get_url_id_classroom_or_raise(classroom_id)

            classwork_list = [
                relation.classwork
                for relation in ClassroomHasClasswork.objects.filter(
                    classroom=classroom_instance
                )
            ]
            resource_list = [
                relation.resource
                for relation in ClassroomHasResource.objects.filter(
                    classroom=classroom_instance
                )
            ]

            classwork_serializer = self.classwork_serializer_class(
                classwork_list, many=True
            )
            resource_serializer = self.resource_serializer_class(
                resource_list, many=True
            )

            return Response(
                data=dict(
                    classworks=classwork_serializer.data,
                    resources=resource_serializer.data,
                ),
                status=200,
            )


class ClassroomClassworkViewSet(ModelViewSet):
    """ """

    serializer_class = ReadClassworkSerializer
    create_serializer_class = CreateClassworkSerializer
    update_serializer_class = UpdateClassworkSerializer
    classroom_serializer = ClassroomOnlySerializer
    attachment_serializer = AttachmentSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticatedCustom]

        if self.action in ["create", "update", "delete"]:
            permission_classes.append(IsClassroomOwnerOrTeacher)

        if self.action in ["read", "list_classworks"]:
            permission_classes.append(IsClassroomMember)

        return [permission() for permission in permission_classes]

    @extend_schema(request=create_serializer_class)
    @try_except_http_error_decorator
    def create(self, *args, **kwargs):
        """Create Classwork"""

        requesting_user = self.request.user
        url_classroom_id = kwargs.get("classroom_id", None)

        if url_classroom_id:
            classroom_instance = get_url_id_classroom_or_raise(url_classroom_id)
            self.check_object_permissions(self.request, classroom_instance)

            serializer = self.create_serializer_class(data=self.request.data)
            serializer.is_valid(raise_exception=True)

            created_classwork = serializer.save(_created_by=requesting_user)

            ClassroomHasClasswork.objects.create(
                classroom=classroom_instance, classwork=created_classwork
            )

            check_and_handle_attachments(self.request, created_classwork)

            # TODO send Email/Notification

            return Response(
                create_200(
                    201,
                    "Created",
                    "Classwork Created",
                    dict(classwork=serializer.data),
                ),
                status=201,
            )

    @try_except_http_error_decorator
    def read(self, *args, **kwargs):
        """Get details for classwork"""

        requesting_user = self.request.user
        url_id_classwork = kwargs.get("classwork_id", None)

        if url_id_classwork:
            classwork_instance = get_url_id_classwork_or_raise(url_id_classwork)
            classwork_classroom = classwork_instance.classwork_classroom.get().classroom

            self.check_object_permissions(self.request, classwork_classroom)

            if classwork_instance.attachments == True:
                attachment_list = ClassworkHasAttachment.objects.filter(
                    classwork=classwork_instance
                )
                attachments = [item.attachment for item in attachment_list]
                attachment_serializer = self.attachment_serializer(
                    attachments, many=True
                )

            serializer = self.serializer_class(classwork_instance)

            return Response(
                data=dict(
                    classwork=serializer.data,
                    attachments=attachment_serializer.data
                    if classwork_instance.attachments
                    else [],
                ),
                status=200,
            )

    @try_except_http_error_decorator
    def list_classworks(self, *args, **kwargs):
        """ """

        url_classroom_id = kwargs.get("classroom_id", None)

        if url_classroom_id:
            classroom_instance = get_url_id_classroom_or_raise(url_classroom_id)
            classroom_classwork = ClassroomHasClasswork.objects.filter(
                classroom=classroom_instance
            )

            classwork_list = [item.classwork for item in classroom_classwork]

            serializer = self.serializer_class(classwork_list, many=True)
            classroom_serializer = self.classroom_serializer(classroom_instance)

            return Response(
                data=dict(
                    classroom=classroom_serializer.data,
                    classworks=serializer.data,
                ),
                status=200,
            )

    @extend_schema(request=update_serializer_class)
    @try_except_http_error_decorator
    def update(self, *args, **kwargs):

        classwork_id = kwargs.get("classwork_id", None)
        if classwork_id:

            classwork_instance = get_url_id_classwork_or_raise()
            classwork_classroom = classwork_instance.classwork_classroom.classroom
            self.check_object_permissions(self.request, classwork_classroom)

            serializer = self.update_serializer_class(data=self.request.data)
            RequestFieldsChecker().check_at_least_one_field_or_raise(
                req_body=self.request.data, field_options=serializer.Meta.fields
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            check_and_handle_attachments(self.request, classwork_instance)

            return Response(
                create_200(
                    200,
                    "Updated",
                    "Classwork Updated",
                    dict(classwork=serializer.data),
                ),
                status=200,
            )

    @try_except_http_error_decorator
    def delete(self, *args, **kwargs):
        classwork_id = kwargs.get("classwork_id", None)
        if classwork_id:

            classwork_instance = get_url_id_classwork_or_raise()
            classwork_classroom = classwork_instance.classwork_classroom.classroom
            self.check_object_permissions(self.request, classwork_classroom)

            classwork_instance.delete()

            return Response(
                create_200(
                    204,
                    "Deleted",
                    "Classwork Deleted",
                ),
                status=204,
            )


class ClassroomResourceViewSet(ModelViewSet):
    """ """

    serializer_class = ReadResourceSerializer
    create_serializer_class = CreateResourceSerializer
    update_serializer_class = UpdateResourceSerializer
    classroom_serializer = ClassroomOnlySerializer
    attachment_serializer = AttachmentSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticatedCustom]

        if self.action in ["create", "update", "delete"]:
            permission_classes.append(IsClassroomOwnerOrTeacher)

        if self.action in ["read", "list_resources"]:
            permission_classes.append(IsClassroomMember)

        return [permission() for permission in permission_classes]

    @extend_schema(request=create_serializer_class)
    @try_except_http_error_decorator
    def create(self, *args, **kwargs):
        """Create Resource"""

        requesting_user = self.request.user
        url_classroom_id = kwargs.get("classroom_id", None)

        if url_classroom_id:
            classroom_instance = get_url_id_classroom_or_raise(url_classroom_id)
            self.check_object_permissions(self.request, classroom_instance)

            serializer = self.create_serializer_class(data=self.request.data)
            serializer.is_valid(raise_exception=True)

            created_resource = serializer.save(_created_by=requesting_user)

            ClassroomHasResource.objects.create(
                classroom=classroom_instance, resource=created_resource
            )

            check_and_handle_attachments(self.request, created_resource)

            # TODO send Email/Notification

            return Response(
                create_200(
                    201,
                    "Created",
                    "Resource Created",
                    dict(resource=serializer.data),
                ),
                status=201,
            )

    @try_except_http_error_decorator
    def read(self, *args, **kwargs):
        """Get details for resource"""

        requesting_user = self.request.user
        url_id_resource = kwargs.get("resource_id", None)

        if url_id_resource:
            resource_instance = get_url_id_resource_or_raise(url_id_resource)
            resource_classroom = resource_instance.resource_classroom.get().classroom

            self.check_object_permissions(self.request, resource_classroom)

            if resource_instance.attachments == True:
                attachment_list = ResourceHasAttachment.objects.filter(
                    resource=resource_instance
                )
                attachments = [item.attachment for item in attachment_list]
                attachment_serializer = self.attachment_serializer(
                    attachments, many=True
                )

            serializer = self.serializer_class(resource_instance)

            return Response(
                data=dict(
                    resource=serializer.data,
                    attachments=attachment_serializer.data
                    if resource_instance.attachments
                    else [],
                ),
                status=200,
            )

    @try_except_http_error_decorator
    def list_resources(self, *args, **kwargs):
        """ """

        url_classroom_id = kwargs.get("classroom_id", None)

        if url_classroom_id:
            classroom_instance = get_url_id_classroom_or_raise(url_classroom_id)
            classroom_resource = ClassroomHasResource.objects.filter(
                classroom=classroom_instance
            )

            resource_list = [item.resource for item in classroom_resource]

            serializer = self.serializer_class(resource_list, many=True)
            classroom_serializer = self.classroom_serializer(classroom_instance)

            return Response(
                data=dict(
                    classroom=classroom_serializer.data,
                    resources=serializer.data,
                ),
                status=200,
            )

    @extend_schema(request=update_serializer_class)
    @try_except_http_error_decorator
    def update(self, *args, **kwargs):
        resource_id = kwargs.get("resource_id", None)
        if resource_id:
            resource_instance = get_url_id_resource_or_raise()

            resource_classroom = resource_instance.resource_classroom.classroom
            self.check_object_permissions(self.request, resource_classroom)

            serializer = self.update_serializer_class(data=self.request.data)
            RequestFieldsChecker().check_at_least_one_field_or_raise(
                req_body=self.request.data, field_options=serializer.Meta.fields
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            check_and_handle_attachments(self.request, resource_instance)

            return Response(
                create_200(
                    200,
                    "Updated",
                    "Resource Updated",
                    dict(resource=serializer.data),
                ),
                status=200,
            )

    @try_except_http_error_decorator
    def delete(self, *args, **kwargs):
        resource_id = kwargs.get("resource_id", None)
        if resource_id:

            resource_instance = get_url_id_resource_or_raise()
            resource_classroom = resource_instance.resource_classroom.classroom
            self.check_object_permissions(self.request, resource_classroom)
            resource_instance.delete()

            return Response(
                create_200(
                    204,
                    "Deleted",
                    "Resource Deleted",
                ),
                status=204,
            )


class ClassworkSubmissionViewSet(ModelViewSet):
    """ """

    serializer_class = ReadSubmissionSerializer
    create_serializer_class = CreateSubmissionSerializer
    update_serializer_class = UpdateSubmissionSerializer
    classwork_serializer = ReadClassworkSerializer
    attachment_serializer = AttachmentSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticatedCustom]

        if self.action in ["create"]:
            permission_classes.append(IsClassroomMember)

        if self.action in ["update", "delete"]:
            permission_classes.append(IsSubmissionOwner)

        if self.action in ["grade"]:
            permission_classes.append(IsClassroomOwnerOrTeacher)

        if self.action in ["read", "list_submissions"]:
            permission_classes.append(IsSubmissionOwnerOrClassroomOwnerOrTeacher)

        return [permission() for permission in permission_classes]

    @extend_schema(request=create_serializer_class)
    @try_except_http_error_decorator
    def create(self, *args, **kwargs):
        """ """

        requesting_user = self.request.user
        url_classwork_id = kwargs.get("classwork_id", None)

        if url_classwork_id:
            classwork_instance = get_url_id_classwork_or_raise(url_classwork_id)
            classwork_classroom = classwork_instance.classwork_classroom.get().classroom

            self.check_object_permissions(self.request, classwork_classroom)

            serializer = self.create_serializer_class(data=self.request.data)
            serializer.is_valid(raise_exception=True)

            created_submission = serializer.save(_created_by=requesting_user)

            ClassworkHasSubmission.objects.create(
                submission=created_submission, classwork=classwork_instance
            )

            check_and_handle_attachments(self.request, created_submission)

            # TODO send Email/Notification

            return Response(
                create_200(
                    201,
                    "Created",
                    "Submission Created",
                    dict(submission=serializer.data),
                ),
                status=201,
            )

    @try_except_http_error_decorator
    def read(self, *args, **kwargs):
        """Get details for submission"""

        url_id_submission = kwargs.get("submission_id", None)

        if url_id_submission:
            submission_instance = get_url_id_submission_or_raise(url_id_submission)
            self.check_object_permissions(self.request, submission_instance)

            if submission_instance.attachments == True:
                attachment_list = SubmissionHasAttachment.objects.filter(
                    submission=submission_instance
                )
                attachments = [item.attachment for item in attachment_list]
                attachment_serializer = self.attachment_serializer(
                    attachments, many=True
                )

            serializer = self.serializer_class(submission_instance)

            return Response(
                data=dict(
                    submission=serializer.data,
                    attachments=attachment_serializer.data
                    if submission_instance.attachments
                    else [],
                ),
                status=200,
            )

    @try_except_http_error_decorator
    def list_submissions(self, *args, **kwargs):
        """ """

        url_classwork_id = kwargs.get("classwork_id", None)

        if url_classwork_id:
            classwork_instance = get_url_id_classwork_or_raise(url_classwork_id)
            classwork_submissions = ClassworkHasSubmission.objects.filter(
                classwork=classwork_instance
            )

            # submissions = Submission.objects.filter(id__in=classwork_submissions)
            submission_list = [item.submission for item in classwork_submissions]

            serializer = self.serializer_class(submission_list, many=True)
            classwork_serializer = self.classwork_serializer(classwork_instance)

            return Response(
                data=dict(
                    classwork=classwork_serializer.data,
                    submissions=serializer.data,
                ),
                status=200,
            )

    @try_except_http_error_decorator
    def list_self_submissions(self, *args, **kwargs):
        """ """

        requesting_user = self.request.user
        url_classwork_id = kwargs.get("classwork_id", None)

        if url_classwork_id:
            classwork_instance = get_url_id_classwork_or_raise(url_classwork_id)
            classwork_submissions = ClassworkHasSubmission.objects.filter(
                classwork=classwork_instance
            ).all()

            submission_id_list = [item.submission.id for item in classwork_submissions]

            self_submissions = Submission.objects.filter(
                Q(id__in=submission_id_list) & Q(_created_by=requesting_user)
            )

            serializer = self.serializer_class(self_submissions, many=True)
            classwork_serializer = self.classwork_serializer(classwork_instance)

            return Response(
                data=dict(
                    classwork=classwork_serializer.data,
                    submissions=serializer.data,
                ),
                status=200,
            )

    @extend_schema(request=update_serializer_class)
    @try_except_http_error_decorator
    def update(self, *args, **kwargs):
        submission_id = kwargs.get("submission_id", None)
        if submission_id:
            submission_instance = get_url_id_submission_or_raise()
            self.check_object_permissions(self.request, submission_instance)

            serializer = self.update_serializer_class(data=self.request.data)
            RequestFieldsChecker().check_at_least_one_field_or_raise(
                req_body=self.request.data, field_options=serializer.Meta.fields
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            check_and_handle_attachments(self.request, submission_instance)

            return Response(
                create_200(
                    200,
                    "Updated",
                    "Resource Updated",
                    dict(resource=serializer.data),
                ),
                status=200,
            )

    @try_except_http_error_decorator
    def grade(self, *args, **kwargs):
        submission_id = kwargs.get("submission_id", None)
        if submission_id:
            submission_instance = get_url_id_submission_or_raise()
            self.check_object_permissions(self.request, submission_instance)

            serializer = self.update_serializer_class(data=self.request.data)
            RequestFieldsChecker().check_required_field_or_raise(
                req_body=self.request.data, field_options=["grade"]
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(
                create_200(
                    200,
                    "Graded",
                    "Resource Graded",
                    dict(resource=serializer.data),
                ),
                status=200,
            )

    @try_except_http_error_decorator
    def delete(self, *args, **kwargs):
        submission_id = kwargs.get("submission_id", None)
        if submission_id:
            submission_instance = get_url_id_submission_or_raise()
            self.check_object_permissions(self.request, submission_instance)
            submission_instance.delete()

            return Response(
                create_200(
                    204,
                    "Deleted",
                    "Submission Deleted",
                ),
                status=204,
            )
