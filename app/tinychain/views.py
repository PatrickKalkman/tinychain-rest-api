from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Alert

from tinychain import serializers


class AlertViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Manage Alerts in the database."""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Alert.objects.all()
    serializer_class = serializers.AlertSerializer

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by(
            '-exchange').order_by('-coinpair')
