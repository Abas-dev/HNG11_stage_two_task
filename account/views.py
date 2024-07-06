from django.shortcuts import get_object_or_404
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from .serializers import non
from rest_framework.permissions import AllowAny,IsAuthenticated
from .models import User 


class SignUp(GenericAPIView):
    serializer_class = ...
    permission_classes = [AllowAny]

   
    def post(self,request:Request):
        data = request.data 

        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            serializer.save()

            response = {
                "message": "User has been created successfully",
                "data": serializer.data
            }

            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
                    "errors": [
                        {
                        "field": "string",
                        "message": serializer.errors
                        },
                    ]
                }
        return Response(data=serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)      