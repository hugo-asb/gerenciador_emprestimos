import datetime
from rest_framework import serializers
from loan_api.dynamic_serializer import DynamicFieldsModelSerializer
from loans.models import Loan


class LoanSerializer(DynamicFieldsModelSerializer):
    total_installments = serializers.SerializerMethodField("get_total_installments")
    total_interest = serializers.SerializerMethodField("get_total_interest")
    total_paid = serializers.SerializerMethodField("get_total_paid")
    outstanding_balance = serializers.SerializerMethodField("get_balance")
    total_debt = serializers.SerializerMethodField("get_total_debt")

    class Meta:
        model = Loan
        fields = (
            "id",
            "user",
            "bank",
            "ip_address",
            "request_date",
            "maturity_date",
            "nominal_value",
            "interest_rate",
            "total_debt",
            "total_installments",
            "total_interest",
            "total_paid",
            "outstanding_balance",
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
                {"detail": "Nominal value must be greater than zero"}
            )
        return nominal_value

    def validate_maturity_date(self, maturity_date):
        if maturity_date <= datetime.date.today():
            raise serializers.ValidationError(
                {"detail": "Loan maturity date must be greater than request date"}
            )
        return maturity_date

    def validate_interest_rate(self, interest_rate):
        if interest_rate <= 0:
            raise serializers.ValidationError(
                {"detail": "Interest rate must be greater than zero"}
            )
        return interest_rate

    def get_total_installments(self, obj):
        return obj.get_total_installments

    def get_total_interest(self, obj):
        return obj.get_total_interest

    def get_total_paid(self, obj):
        return obj.get_total_paid

    def get_balance(self, obj):
        return obj.get_balance

    def get_total_debt(self, obj):
        return obj.get_total_debt
