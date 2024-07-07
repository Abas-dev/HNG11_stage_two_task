from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .serializers import *
from .models import *
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


class UserRegistrationView(APIView):
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            token = RefreshToken.for_user(user)
            return Response({'status': 'success',
                             'message': 'User successfully registered',
                             'data': {'accessToken': str(token.access_token),
                                      'user': UserSerializer(user).data}},
                            status=status.HTTP_201_CREATED)
        return Response({
            'errors': [
                {
                    'field': list(serializer.errors.keys())[0],
                    'message': serializer.errors[list(serializer.errors.keys())[0]][0]
                }
            ]
        }, status=422)


class UserLoginView(APIView):
    serializer_class = LoginSerializer

    def post(self, request, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({
                'errors': [
                    {
                        'field': list(serializer.errors.keys())[0],
                        'message': serializer.errors[list(serializer.errors.keys())[0]][0]
                    }
                ]
            }, status=422)
        validated_data = serializer.validated_data
        email = validated_data["email"]
        password = validated_data["password"]
        user = authenticate(request, email=email, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            tokens = {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
            data = {
                "accessToken": tokens['access'],
                "user": {
                    "userId": str(user.user_id),
                    "firstName": user.first_name,
                    "lastName": user.last_name,
                    "email": user.email,
                    "phone": user.phone,
                }
            }
            return Response({
                "status": "success",
                "message": "Login successful",
                "data": data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'errors': [
                    {
                        'field': 'email/password',
                        'message': 'Authentication failed'
                    }
                ]
            }, status=status.HTTP_401_UNAUTHORIZED)


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request, pk):
        user = User.objects.filter(pk=pk, user_id=request.user.user_id).first()

        if user and user.user_id == request.user.user_id:
            serializer = self.serializer_class(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({
            'status': 'Not found',
            'message': 'User not found',
            'statusCode': 404
        }, status=status.HTTP_404_NOT_FOUND)


class OrganizationListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrganisationSerializer

    def get(self, request):
        organizations = Organization.objects.filter(users=request.user)
        return Response({
            'status': 'success',
            'data': self.serializer_class(organizations, many=True).data
        }, status=status.HTTP_200_OK)


class OrganizationDetailsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrganisationSerializer

    def get(self, request, pk):
        try:
            org_uuid = uuid.UUID(pk)
        except ValueError:
            return Response({
                'status': 'Bad Request',
                'message': 'Invalid UUID format for organization ID',
                'statusCode': 400
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            organization = Organization.objects.get(org_id=org_uuid, users=request.user)
            serializer = self.serializer_class(organization)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Organization.DoesNotExist:
            return Response({
                'status': 'Not Found',
                'message': 'Organization not found',
                'statusCode': 404
            }, status=status.HTTP_404_NOT_FOUND)


class OrganizationCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrganisationCreateSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            org = serializer.save()
            Membership.objects.create(user=request.user, organization=org)
            return Response({
                'status': 'success',
                'message': 'Organisation created successfully',
                'data': self.serializer_class(org).data
            }, status=status.HTTP_201_CREATED)
        return Response({
                'status': 'Bad request',
                'message': 'Invalid data',
                'statusCode': 400,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class AddUserToOrganizationView(APIView):
    def post(self, request, org_id):
        user_id = request.data.get('userId')
        if not user_id:
            return Response({"status": "error", "message": "userId is required"}, status=status.HTTP_400_BAD_REQUEST)

        organization = get_object_or_404(Organization, org_id=org_id)
        user = get_object_or_404(User, user_id=user_id)

        Membership.objects.create(user=user, organization=organization)

        return Response({"status": "success", "message": "User added to organisation successfully"},
                        status=status.HTTP_200_OK)