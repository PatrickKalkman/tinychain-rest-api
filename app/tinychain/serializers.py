from rest_framework import serializers

from core.models import Alert, DeviceToken


class AlertSerializer(serializers.ModelSerializer):
    """Serializer for Alert objects"""

    class Meta:
        model = Alert
        fields = ('id', 'exchange', 'coinpair', 'indicator', 'limit',)
        read_only_fields = ('id',)


class DeviceTokenSerializer(serializers.ModelSerializer):
    """Serializer for DeviceToken objects"""

    class Meta:
        model = DeviceToken
        fields = ('id', 'token', 'device_type',)
        read_only_fields = ('id',)
