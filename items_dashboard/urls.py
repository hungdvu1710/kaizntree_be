from django.urls import path
from . import views

urlpatterns = [
    path("", views.Item_Dashboard.as_view(), name="items"),
]
