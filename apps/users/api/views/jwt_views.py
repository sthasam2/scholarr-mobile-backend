# from drf_yasg import openapi
# from drf_yasg.utils import swagger_auto_schema
from apps.core.exceptions import CustomAuthenticationFailed
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import (
    TokenError,
    InvalidToken,
    AuthenticationFailed,
)
from apps.core.helpers import create_400, create_500

from ..schemas import LoginAcceptedResponseSchema, Response400Schema, Response500Schema
from ..serializers import CustomTokenObtainPairSerializer

##################################
##          RETRIEVE
##################################


class CustomTokenObtainPairView(TokenObtainPairView):
    """ """

    serializer_class = CustomTokenObtainPairSerializer

    # @swagger_auto_schema(
    #     responses={
    #         HTTP_401_UNAUTHORIZED: openapi.Response(
    #             description="Access Denied", schema=Response400Schema
    #         ),
    #         HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(
    #             description="Internal Error", schema=Response500Schema
    #         ),
    #         HTTP_200_OK: openapi.Response(
    #             description="Login Accepted", schema=LoginAcceptedResponseSchema
    #         ),
    #     },
    # )
    def post(self, request, *args, **kwargs):
        """
        POST method for jwt  tokens
        """

        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            context = serializer.validated_data

            if not context["user_details"]["email_verified"]:

                return Response(
                    data=create_400(401, "Access Denied!", "Email not verified!"),
                    status=HTTP_401_UNAUTHORIZED,
                )

            else:
                return Response(serializer.validated_data, status=200)

        except TokenError as e:
            raise InvalidToken(e.args[0])

        except CustomAuthenticationFailed as error:
            return Response(error.message, status=error.message["status"])

        except Exception as error:
            return Response(
                create_500(
                    verbose=f"Could not send reset account password email due to an unknown error.",
                    cause=error.args[0] or None,
                ),
                status=500,
            )

        # context = super().post(request, *args, **kwargs)

        # if not context.data["user_details"]["email_verified"]:

        #     return Response(
        #         data=create_400(401, "Access Denied!", "Email not verified!"),
        #         status=HTTP_401_UNAUTHORIZED,
        #     )
        # else:
        #     return context
