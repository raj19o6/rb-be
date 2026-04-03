from rest_framework import serializers
from django.contrib.auth.models import Group


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

    def validate_name(self, value):
        qs = Group.objects.filter(name__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A role with this name already exists.")
        return value
