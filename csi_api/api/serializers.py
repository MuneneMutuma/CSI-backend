from rest_framework import serializers


class QuerySerializer(serializers.Serializer):
    query = serializers.CharField(max_length=256)
    
    def validate(self, data):
        return data