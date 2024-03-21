from rest_framework import serializers
from payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"

    def create(self, validated_data):
        if self.is_valid():
            return Payment.objects.create(**validated_data)

    def update(self, instance, validated_data):
        if self.is_valid():
            instance.date = validated_data.get("date", instance.date)
            instance.value = validated_data.get("value", instance.value)
            instance.save()
            return instance

    def validate_value(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                {"message": "Payment value must be greater than zero"}
            )
        return value
