# api_contact/urls.py
from django.urls import path
from .views import ContactCreateView, ContactListView, ContactDetailView

urlpatterns = [
    path('',           ContactCreateView.as_view()),  # POST
    path('list/',      ContactListView.as_view()),     # GET（管理者）
    path('<int:pk>/',  ContactDetailView.as_view()),   # GET/PATCH/DELETE（管理者）
]
