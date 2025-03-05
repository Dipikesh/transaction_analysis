from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'uploads', views.TransactionUploadViewSet)

urlpatterns = [
    path('', include(router.urls)),
]