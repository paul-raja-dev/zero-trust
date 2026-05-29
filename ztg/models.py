from django.db import models


class RequestLog(models.Model):

    method = models.CharField(max_length=10)
    path = models.CharField(max_length=200)
    status_code = models.IntegerField()
    ip_address = models.CharField(max_length=100)
    user_agent = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f'{self.method} {self.path}'


class BlockedIP(models.Model):

    ip_address = models.CharField(max_length=50,unique=True)
    reason = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    blocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-blocked_at']
    
    def __str__(self):  
        return f'{self.ip_address} {self.blocked_at}'