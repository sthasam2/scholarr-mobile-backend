# from django.shortcuts import render

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HomeView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):
        """
        GET method at route `api/`
        """
        content = {"message": "Welcome to Bumblebee API!"}
        return Response(content)
