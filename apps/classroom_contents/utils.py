from apps.classroom_contents.api.serializers import AttachmentSerializer
from apps.classroom_contents.models import (
    Classwork,
    ClassworkHasAttachment,
    Resource,
    ResourceHasAttachment,
    Submission,
    SubmissionHasAttachment,
)
from apps.core.exceptions import (
    LimitExceededError,
    MissingFieldsError,
    NoneExistenceError,
    UrlParameterError,
)


def check_and_handle_attachments(request, classroom_content_instance):
    """"""

    attachment_list = request.data.getlist("attachments", None)

    if attachment_list:

        if len(attachment_list) == 0:
            raise MissingFieldsError(
                cause="Attachment handling",
                message="Missing Fields",
                verbose="Request body `attachments` field contains no files. Please provide `attachments`",
                status_code=400,
            )

        if len(attachment_list) > 8:
            raise LimitExceededError(
                cause="Attachment handling",
                message="Limit Exceeded",
                verbose="Request body doesn't contains more than 8 `attachments` field. Max limit is 8`",
                status_code=400,
            )

        for attachment in attachment_list:
            attachment_serializer = AttachmentSerializer(
                data=dict(attachment=attachment)
            )

            if attachment_serializer.is_valid(raise_exception=True):
                file_type = attachment.content_type

                created_attachment = attachment_serializer.save(
                    mime_type=file_type,
                    **attachment_serializer.validated_data,
                )

                if isinstance(classroom_content_instance, Classwork):
                    ClassworkHasAttachment.objects.create(
                        classwork=classroom_content_instance,
                        attachment=created_attachment,
                    )
                if isinstance(classroom_content_instance, Resource):
                    ResourceHasAttachment.objects.create(
                        resource=classroom_content_instance,
                        attachment=created_attachment,
                    )
                if isinstance(classroom_content_instance, Submission):
                    SubmissionHasAttachment.objects.create(
                        submission=classroom_content_instance,
                        attachment=created_attachment,
                    )

        classroom_content_instance.attachments = True
        classroom_content_instance.save()


def get_url_id_classwork_or_raise(id=None):
    """ """

    if id:
        try:
            return Classwork.objects.get(id=id)

        except (TypeError, ValueError, OverflowError, Classwork.DoesNotExist):
            raise NoneExistenceError(
                cause="Classwork",
                status_code=400,
                message="Non existence",
                verbose=f"Classwork(id={id}) does not exist!",
            )

    else:
        raise UrlParameterError(
            cause="Classwork id in URL",
            status_code=400,
            message="URL parameter wrong",
            verbose="[id] must be provided!",
        )


def get_url_id_resource_or_raise(id=None):
    """ """

    if id:
        try:
            return Resource.objects.get(id=id)

        except (TypeError, ValueError, OverflowError, Resource.DoesNotExist):
            raise NoneExistenceError(
                cause="Resource",
                status_code=400,
                message="Non existence",
                verbose=f"Resource(id={id}) does not exist!",
            )

    else:
        raise UrlParameterError(
            cause="Resource id in URL",
            status_code=400,
            message="URL parameter wrong",
            verbose="[id] must be provided!",
        )


def get_url_id_submission_or_raise(id=None):
    """ """

    if id:
        try:
            return Submission.objects.get(id=id)

        except (TypeError, ValueError, OverflowError, Submission.DoesNotExist):
            raise NoneExistenceError(
                cause="Resource",
                status_code=400,
                message="Non existence",
                verbose=f"Resource(id={id}) does not exist!",
            )

    else:
        raise UrlParameterError(
            cause="Submission id in URL",
            status_code=400,
            message="URL parameter wrong",
            verbose="[id] must be provided!",
        )
