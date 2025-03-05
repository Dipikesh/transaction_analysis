from rest_framework import serializers
from .models import TransactionUpload, Transaction

class TransactionUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionUpload
        fields = ['id', 'upload_time', 'status', 'result', 'file']
        read_only_fields = ['id', 'upload_time', 'status', 'result']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['transaction_id', 'date', 'amount', 'category']