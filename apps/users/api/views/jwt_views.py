from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.core.decorators import try_except_http_error_decorator
from apps.core.exceptions import CustomAuthenticationFailed

from ..serializers import CustomTokenObtainPairSerializer

##################################
##          RETRIEVE
##################################


class CustomTokenObtainPairView(TokenObtainPairView):
    """ """

    serializer_class = CustomTokenObtainPairSerializer

    @try_except_http_error_decorator
    def post(self, request, *args, **kwargs):
        """
        POST method for jwt  tokens
        """

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        context = serializer.validated_data

        if not context["user_details"]["email_verified"]:

            raise CustomAuthenticationFailed(
                status_code=401,
                message="Access Denied!",
                verbose="Email not verified!",
                cause="Login",
            )

        else:
            return Response(serializer.validated_data, status=200)
