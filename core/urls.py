from django.contrib import admin
from django.urls import path

from ztg.views import dashboard_api
from ztg.views.auth import login, refresh
from ztg.views.dashboard import dashboard_view

urlpatterns = [
    path('admin/', admin.site.urls),

    # dashboard page
    path('', dashboard_view, name='dashboard'),

    # auth
    path('api/login/', login, name='login'),
    path('api/refresh/', refresh, name='refresh'),

    # dashboard api
    path('api/stats/', dashboard_api.stats, name='api-stats'),
    path('api/requests/', dashboard_api.recent_requests, name='api-requests'),
    path('api/threats/', dashboard_api.threats, name='api-threats'),
    path('api/traffic/', dashboard_api.traffic_chart, name='api-traffic'),
    path('api/threat-breakdown/', dashboard_api.threat_breakdown, name='api-threat-breakdown'),
    path('api/top-ips/', dashboard_api.top_ips, name='api-top-ips'),
    path('api/blocked-ips/', dashboard_api.blocked_ips, name='api-blocked-ips'),
    path('api/block-ip/', dashboard_api.block_ip, name='api-block-ip'),
    path('api/unblock-ip/<int:ip_id>/', dashboard_api.unblock_ip, name='api-unblock-ip'),
    path('api/resolve-threat/<int:threat_id>/', dashboard_api.resolve_threat, name='api-resolve-threat'),
]
