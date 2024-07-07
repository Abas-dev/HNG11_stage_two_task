from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import *

from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, ValidationError):
        custom_response = {
            "errors": [
                {
                    "field": list(exc.detail.keys())[0],
                    "message": exc.detail[list(exc.detail.keys())[0]][0]
                }
            ]
        }
        return Response(custom_response, status=422)

    return response


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email', 'phone']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'phone']

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone = validated_data['phone'],
            password=validated_data['password']
        )
        org_name = f"{validated_data['first_name']}'s Organization"
        organization = Organization.objects.create(name=org_name)
        Membership.objects.create(user=user, organization=organization)
        return user

    def validate(self, data):
        validate_email_format(data.get('email'))
        return data

    def to_representation(self, instance):
        return {
            "userId": str(instance.user_id),
            "firstName": instance.first_name,
            "lastName": instance.last_name,
            "email": instance.email,
            "phone": instance.phone
        }


class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['org_id', 'name', 'description']


class OrganisationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['name', 'description']


class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = ['user', 'organization']


def validate_email_format(email):
    if not email or '@' not in email:
        raise serializers.ValidationError("Enter a valid email address.")
    return email


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=150, min_length=6, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        validate_email_format(email)
        return attrs

