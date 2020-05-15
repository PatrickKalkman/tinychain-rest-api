from rest_framework import serializers

from core.models import Alert


class AlertSerializer(serializers.ModelSerializer):
    """Serializer for Alert objects"""

    class Meta:
        model = Alert
        fields = ('id', 'exchange', 'coinpair', 'indicator', 'limit',)
        read_only_fields = ('id',)
