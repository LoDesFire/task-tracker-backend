from rest_framework import serializers


class InviteOutputSerializer(serializers.Serializer):
    invitation_id = serializers.UUIDField(required=True)
    expires_at = serializers.DateTimeField(required=True)
