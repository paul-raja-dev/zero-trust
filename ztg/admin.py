from django.contrib import admin
from .models import RequestLog,BlockedIP


admin.site.register(RequestLog)
admin.site.register(BlockedIP)