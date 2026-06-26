from django.db import models


class RequestLog(models.Model):

    method = models.CharField(max_length=10)
    path = models.CharField(max_length=200)
    status_code = models.IntegerField()
    ip_address = models.CharField(max_length=100)
    user_agent = models.CharField(max_length=500, blank=True, default='')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f'{self.method} {self.path}'


class BlockedIP(models.Model):

    ip_address = models.CharField(max_length=50, unique=True)
    reason = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    blocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-blocked_at']

    def __str__(self):
        return f'{self.ip_address} - {self.reason}'


class RateLimitViolation(models.Model):

    ip_address = models.CharField(max_length=100)
    path = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.ip_address} hit limit on {self.path}'


class ThreatEvent(models.Model):

    THREAT_TYPES = [
        ('brute_force', 'Brute Force'),
        ('rate_abuse', 'Rate Limit Abuse'),
        ('path_scan', 'Path Scanning'),
        ('blocked_access', 'Blocked IP Access'),
        ('anomaly', 'Anomaly'),
    ]

    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    threat_type = models.CharField(max_length=20, choices=THREAT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='low')
    ip_address = models.CharField(max_length=100)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'[{self.severity.upper()}] {self.threat_type} from {self.ip_address}'