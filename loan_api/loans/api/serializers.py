from rest_framework import serializers
from loans.models import Loan


class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = (
            "id",
            "nominal_value",
            "interest_rate",
            "ip_address",
            "request_date",
            "bank",
            "user",
        )
        read_only_fields = ("id", "user", "ip_address", "request_date")

    def create(self, validated_data):
        if self.is_valid():
            validated_data["user"] = self.context["request"].user
            validated_data["ip_address"] = self.context.get("request").META.get(
                "REMOTE_ADDR"
            )
            return Loan.objects.create(**validated_data)

    def update(self, instance, validated_data):
        if self.is_valid():
            instance.nominal_value = validated_data.get(
                "nominal_value", instance.nominal_value
            )
            instance.interest_rate = validated_data.get(
                "interest_rate", instance.interest_rate
            )
            instance.save()
            return instance

    def validate_nominal_value(self, nominal_value):
        if nominal_value <= 0:
            raise serializers.ValidationError(
                {"message": "Nominal value must be greater than zero"}
            )
        return nominal_value
