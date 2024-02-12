from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from .serializers import SignUpSerializer
from .tokens import create_jwt_pair_for_user

# Create your views here.


@api_view(["POST"])
@permission_classes([])
def sign_up(request: Request):
    data = request.data

    serializer = SignUpSerializer(data=data)

    if serializer.is_valid():
        serializer.save()

        response = {"message": "User Created Successfully", "data": serializer.data}

        return Response(data=response, status=status.HTTP_201_CREATED)

    return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([])
def log_in(request: Request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)

    if user is not None:

        tokens = create_jwt_pair_for_user(user)

        response = {"message": "Login Successfull", "tokens": tokens}
        return Response(data=response, status=status.HTTP_200_OK)

    else:
        return Response(data={"message": "Invalid username or password"})
