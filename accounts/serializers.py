from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['userId', 'firstName', 'lastName', 'email', 'phone']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['firstName', 'lastName', 'email', 'password', 'phone']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            firstName=validated_data['firstName'],
            lastName=validated_data['lastName'],
            phone = validated_data['phone'],
            password=validated_data['password']
        )
        org_name = f"{validated_data['firstName']}'s Organization"
        organization = Organization.objects.create(name=org_name)
        Membership.objects.create(user=user, organization=organization)
        return user

    def validate(self, data):
        validate_email_format(data.get('email'))
        return data

    def to_representation(self, instance):
        return {
            "userId": str(instance.userId),
            "firstName": instance.firstName,
            "lastName": instance.lastName,
            "email": instance.email,
            "phone": instance.phone
        }


class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['orgId', 'name', 'description']


class OrganisationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["orgId",'name', 'description']


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