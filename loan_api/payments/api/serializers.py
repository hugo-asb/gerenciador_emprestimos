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

    def validate(self, data):
        if data["date"] < data["loan"].request_date:
            raise serializers.ValidationError(
                {"detail": "Only payments past loan request date are acceptable"}
            )

        if data["date"] > data["loan"].maturity_date:
            raise serializers.ValidationError(
                {"detail": "Payments past loan maturity date are not acceptable"}
            )

        if data["value"] > data["loan"].get_balance:
            raise serializers.ValidationError(
                {"detail": "Payments can not be bigger than total debt"}
            )

        if data["value"] + data["loan"].get_total_paid > data["loan"].get_balance:
            raise serializers.ValidationError(
                {"detail": "Total payments exceed total debt value"}
            )

        return data

    def validate_value(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                {"detail": "Payment value must be greater than zero"}
            )
        return value
