from rest_framework import serializers

class SMSSerializer(serializers.Serializer):
    phone = serializers.IntegerField()
            
    content = serializers.CharField(max_length=200)

    def validate(self, data):

        print(data['phone'])
    
        if len(str(data['phone'])) < 10 or len(str(data['phone'])) > 12:
            raise serializers.ValidationError("wrong phone")
        return data