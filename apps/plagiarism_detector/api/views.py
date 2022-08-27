from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.decorators import try_except_http_error_decorator
from apps.core.permissions import IsAuthenticatedCustom
from apps.plagiarism_detector.api.serializer import PlagiarismSerializer
from apps.plagiarism_detector.models import PlagiarismInfo


class PlagiarismListView(APIView):
    """ """

    serializer_class = PlagiarismSerializer
    permission_classes = [IsAuthenticatedCustom]

    @try_except_http_error_decorator
    def get(self, request, *args, **kwargs):
        """ """

        url_submissionId = kwargs.get("submission_id", None)

        if url_submissionId:
            plagiarism_list = PlagiarismInfo.objects.filter(
                Q(submission_agent=url_submissionId)
                | Q(submission_target=url_submissionId)
            )

            serializer = self.serializer_class(plagiarism_list, many=True)

        return Response(dict(plagiarism=serializer.data), status=status.HTTP_200_OK)
