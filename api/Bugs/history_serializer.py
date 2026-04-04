from rest_framework import serializers
from api.Bugs.history_model import BugsHistory


class BugsHistorySerializer(serializers.ModelSerializer):
    changed_by_username = serializers.CharField(source='changed_by.username', read_only=True)

    class Meta:
        model = BugsHistory
        fields = '__all__'
