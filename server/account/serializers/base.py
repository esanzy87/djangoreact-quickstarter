from rest_framework import serializers


class BaseModelSerializer(serializers.ModelSerializer):
    created = serializers.ReadOnlyField()
    updated = serializers.ReadOnlyField()
    created_by = serializers.ReadOnlyField()
    updated_by = serializers.ReadOnlyField()
    deleted_by = serializers.ReadOnlyField()
    
    def create(self, validated_data):
        instance = super().create(validated_data)
        try:
            user = self.context['request'].user
            if user.is_authenticated:
                instance.created_by = user.email
                instance.updated_by = user.email
                instance.save()
        except KeyError:
            pass
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        try:
            user = self.context['request'].user
            if user.is_authenticated:
                instance.updated_by = user.email
                instance.save()
        except KeyError:
            pass
        return instance
