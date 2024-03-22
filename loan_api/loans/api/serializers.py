import datetime
from rest_framework import serializers
from loans.models import Loan


class LoanSerializer(serializers.ModelSerializer):
    total_installments = serializers.SerializerMethodField("get_total_installments")

    class Meta:
        model = Loan
        fields = (
            "id",
            "nominal_value",
            "interest_rate",
            "ip_address",
            "request_date",
            "maturity_date",
            "bank",
            "user",
            "total_installments",
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

    def validate(self, data):
        if data["maturity_date"] <= datetime.date.today():
            raise serializers.ValidationError(
                {"detail": "Loan maturity date must be greater than request date"}
            )
        return data

    def validate_nominal_value(self, nominal_value):
        if nominal_value <= 0:
            raise serializers.ValidationError(
                {"message": "Nominal value must be greater than zero"}
            )
        return nominal_value

    def get_total_installments(self, obj):
        return obj.get_total_installments
