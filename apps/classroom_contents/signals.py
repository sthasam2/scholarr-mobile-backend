from venv import create
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.classroom_contents.models import Attachment, SubmissionHasAttachment

from apps.plagiarism_detector.utils import (
    check_plagiarism,
    create_model,
    joblib_dump,
    open_file,
)
from configs.definitions import DEBUG


# @receiver(post_save, sender=Attachment)
# def profile_post_save(sender, instance, created, **kwargs):
#     """
#     Reciever function for Attachment model post save
#     """

#     if DEBUG:
#         print("Attachment `post_save` signal received!")

#     if created:
#         attachment_path = instance.attachment.path
#         content_type = instance.mime_type

#         text = open_file(attachment_path, content_type)
#         tokenized_data, model = create_model(text)
#         dump_tokenized_filepath = joblib_dump(tokenized_data)
#         dump_model_filepath = joblib_dump(model)

#         instance.tokenized_dump = dump_tokenized_filepath
#         instance.model_dump = dump_model_filepath
#         instance.save()

#         check_plagiarism(instance)

#         print("Done")


@receiver(post_save, sender=SubmissionHasAttachment)
def profile_post_save(sender, instance, created, **kwargs):
    """
    Reciever function for Attachment model post save
    """

    if DEBUG:
        print("Attachment `post_save` signal received!")

    if created:
        attachment = instance.attachment
        submission = instance.submission

        attachment_path = attachment.attachment.path
        content_type = attachment.mime_type

        text = open_file(attachment_path, content_type)
        tokenized_data, model = create_model(text)
        dump_tokenized_filepath = joblib_dump(tokenized_data)
        dump_model_filepath = joblib_dump(model)

        attachment.tokenized_dump = dump_tokenized_filepath
        attachment.model_dump = dump_model_filepath
        attachment.save()

        check_plagiarism(attachment, submission)
        

        print("Done")
