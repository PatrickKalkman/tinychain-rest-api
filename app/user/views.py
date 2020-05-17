from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from user.serializers import UserSerializer, AuthTokenSerializer
from core.models import User


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for the user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class ValidateApiView(APIView):

    def get(self, request, format=None):
        verification_id = request.query_params.get('verification_id')
        if verification_id:
            users = User.objects.filter(verification_id=verification_id)
            if users.count() == 1:
                user = users[0]
                user.verified = True
                user.save()
                return Response({'message': 'User is verified'})

        return Response({'message': 'invalid request'},
                        status=status.HTTP_400_BAD_REQUEST)
