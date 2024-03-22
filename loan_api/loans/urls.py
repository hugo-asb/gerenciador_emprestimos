from django.urls import path, include
from rest_framework.routers import DefaultRouter
from loans.api.viewsets import LoanViewSet
from loans import views


router = DefaultRouter()
router.register("list", LoanViewSet, basename="Loan list")

urlpatterns = [
    path("", views.LoanPost.as_view(), name="Create new loan"),
    path("<int:id>/", views.LoanView.as_view(), name="Create new loan"),
    path("", include(router.urls)),
]
