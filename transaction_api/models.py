from django.db import models

class TransactionUpload(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.AutoField(primary_key=True)
    upload_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    result = models.JSONField(null=True, blank=True)
    file = models.FileField(upload_to='uploads/')

    def __str__(self):
        return f"Upload {self.id} - {self.status}"

class Transaction(models.Model):
    transaction_id = models.CharField(max_length=100, unique=True)
    date = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    upload = models.ForeignKey(TransactionUpload, on_delete=models.CASCADE, related_name='transactions')

    def __str__(self):
        return f"Transaction {self.transaction_id}"