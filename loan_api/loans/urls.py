from django.urls import path
from loans import views


urlpatterns = [
    path("", views.LoanPost.as_view(), name="Create new loan"),
    path("<int:id>", views.LoanView.as_view(), name="Create new loan"),
    path("list", views.LoanList.as_view(), name="List all users loans"),
]
