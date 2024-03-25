from django.urls import path, include
from rest_framework.routers import DefaultRouter
from loans.api.viewsets import LoanViewSet
from loans import views


router = DefaultRouter()
router.register("list", LoanViewSet, basename="loan_list")

urlpatterns = [
    path("", views.LoanPost.as_view(), name="create_new_loan"),
    path("<int:id>/", views.LoanView.as_view(), name="loan_get_patch_delete"),
    path(
        "<int:id>/outstanding_balance/",
        views.GetOutstandingBalance.as_view(),
        name="loan_get_outstanding_balance",
    ),
    path("", include(router.urls)),
]
