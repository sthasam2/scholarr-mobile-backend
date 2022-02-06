from rest_framework import serializers


class ResponseSerializer(serializers.Serializer):
    pass


class UserLoginDetails(ResponseSerializer):
    username = serializers.CharField()
    email = serializers.CharField()
    id = serializers.IntegerField()
    email_verified = serializers.BooleanField()


class MessageDetail(ResponseSerializer):
    message = serializers.CharField(label="message of the response")
    detail = serializers.CharField(label="detailed message of response")


class Response400Schema(ResponseSerializer):
    status = serializers.IntegerField(label="status code of response")
    error = MessageDetail()


class Response200Schema(ResponseSerializer):
    status = serializers.IntegerField(label="status code of response")
    success = MessageDetail()


class Response500Schema(ResponseSerializer):
    status = serializers.IntegerField(label="status code of response")
    error = MessageDetail()


class LoginAcceptedResponseSchema(ResponseSerializer):
    access = serializers.IntegerField(label="status code of response")
    refresh = serializers.CharField(label="message of the response")
    user_details = UserLoginDetails()
