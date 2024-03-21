from django.urls import path, include
from rest_framework.routers import DefaultRouter
from payments.api.viewsets import ListAllPaymentsViewSet, ListPaymentsByLoanViewSet
from payments import views


router = DefaultRouter()
router.register("list_all", ListAllPaymentsViewSet, basename="list_all_payments")
router.register(
    "list/(?P<loan_id>[^/.]+)",
    ListPaymentsByLoanViewSet,
    basename="list_payments_by_loan_id",
)

urlpatterns = [
    path("", views.PaymentPost.as_view(), name="post_payment"),
    path("<int:id>", views.PaymentView.as_view(), name="payment_methods"),
    path("", include(router.urls)),
]
