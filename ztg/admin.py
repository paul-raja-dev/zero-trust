from django.contrib import admin
from .models import RequestLog, BlockedIP, RateLimitViolation, ThreatEvent


admin.site.register(RequestLog)
admin.site.register(BlockedIP)
admin.site.register(RateLimitViolation)
admin.site.register(ThreatEvent)