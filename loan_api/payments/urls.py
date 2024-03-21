from django.urls import path, include
from rest_framework.routers import DefaultRouter
from payments.api.viewsets import PaymentViewSet
from payments import views


router = DefaultRouter()
router.register("list", PaymentViewSet, basename="Payment list")

urlpatterns = [
    path("", views.PaymentPost.as_view(), name="Create new payment"),
    path("<int:id>", views.PaymentView.as_view(), name="Payment get, patch and delete"),
    path("", include(router.urls)),
]
