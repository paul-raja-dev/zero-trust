from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from django.db.models.functions import TruncHour, TruncDate
from django.utils import timezone
from datetime import timedelta
import json

from ztg.models import RequestLog, BlockedIP, RateLimitViolation, ThreatEvent


def stats(request):
    """overview stats for the dashboard cards"""

    now = timezone.now()
    last_24h = now - timedelta(hours=24)

    total_requests = RequestLog.objects.filter(timestamp__gte=last_24h).count()
    blocked_count = BlockedIP.objects.filter(is_active=True).count()
    violations_count = RateLimitViolation.objects.filter(timestamp__gte=last_24h).count()
    threats_count = ThreatEvent.objects.filter(
        timestamp__gte=last_24h, is_resolved=False
    ).count()

    # requests in the last hour vs previous hour for trend
    last_hour = RequestLog.objects.filter(timestamp__gte=now - timedelta(hours=1)).count()
    prev_hour = RequestLog.objects.filter(
        timestamp__gte=now - timedelta(hours=2),
        timestamp__lt=now - timedelta(hours=1)
    ).count()

    return JsonResponse({
        'total_requests': total_requests,
        'blocked_ips': blocked_count,
        'rate_violations': violations_count,
        'active_threats': threats_count,
        'requests_last_hour': last_hour,
        'requests_prev_hour': prev_hour,
    })


def recent_requests(request):
    """paginated recent request logs"""

    limit = int(request.GET.get('limit', 50))
    offset = int(request.GET.get('offset', 0))

    logs = RequestLog.objects.all()[offset:offset + limit]

    data = [{
        'id': log.id,
        'method': log.method,
        'path': log.path,
        'status_code': log.status_code,
        'ip_address': log.ip_address,
        'user_agent': log.user_agent,
        'timestamp': log.timestamp.isoformat(),
    } for log in logs]

    total = RequestLog.objects.count()

    return JsonResponse({'results': data, 'total': total})


def threats(request):
    """recent threat events"""

    limit = int(request.GET.get('limit', 20))
    events = ThreatEvent.objects.all()[:limit]

    data = [{
        'id': e.id,
        'threat_type': e.threat_type,
        'severity': e.severity,
        'ip_address': e.ip_address,
        'description': e.description,
        'timestamp': e.timestamp.isoformat(),
        'is_resolved': e.is_resolved,
    } for e in events]

    return JsonResponse({'results': data})


def traffic_chart(request):
    """hourly traffic data for the last 24 hours"""

    now = timezone.now()
    last_24h = now - timedelta(hours=24)

    hourly = (
        RequestLog.objects
        .filter(timestamp__gte=last_24h)
        .annotate(hour=TruncHour('timestamp'))
        .values('hour')
        .annotate(count=Count('id'))
        .order_by('hour')
    )

    data = [{
        'hour': entry['hour'].isoformat(),
        'count': entry['count'],
    } for entry in hourly]

    return JsonResponse({'results': data})


def threat_breakdown(request):
    """threat counts grouped by type — for the doughnut chart"""

    breakdown = (
        ThreatEvent.objects
        .values('threat_type')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    data = [{
        'type': entry['threat_type'],
        'count': entry['count'],
    } for entry in breakdown]

    return JsonResponse({'results': data})


def top_ips(request):
    """top IPs by request count"""

    top = (
        RequestLog.objects
        .values('ip_address')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )

    data = [{
        'ip': entry['ip_address'],
        'count': entry['count'],
    } for entry in top]

    return JsonResponse({'results': data})


def blocked_ips(request):
    """list all blocked IPs"""

    ips = BlockedIP.objects.filter(is_active=True)

    data = [{
        'id': ip.id,
        'ip_address': ip.ip_address,
        'reason': ip.reason,
        'blocked_at': ip.blocked_at.isoformat(),
    } for ip in ips]

    return JsonResponse({'results': data})


@csrf_exempt
@require_http_methods(["POST"])
def block_ip(request):
    """block a new IP"""

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'invalid json'}, status=400)

    ip = body.get('ip_address', '').strip()
    reason = body.get('reason', 'Manually blocked from dashboard')

    if not ip:
        return JsonResponse({'error': 'ip_address is required'}, status=400)

    obj, created = BlockedIP.objects.get_or_create(
        ip_address=ip,
        defaults={'reason': reason, 'is_active': True}
    )

    if not created and not obj.is_active:
        obj.is_active = True
        obj.reason = reason
        obj.save()

    return JsonResponse({
        'id': obj.id,
        'ip_address': obj.ip_address,
        'reason': obj.reason,
        'created': created,
    }, status=201)


@csrf_exempt
@require_http_methods(["POST"])
def unblock_ip(request, ip_id):
    """unblock an IP"""

    try:
        ip = BlockedIP.objects.get(id=ip_id)
    except BlockedIP.DoesNotExist:
        return JsonResponse({'error': 'not found'}, status=404)

    ip.is_active = False
    ip.save()

    return JsonResponse({'message': f'{ip.ip_address} unblocked'})


@csrf_exempt
@require_http_methods(["POST"])
def resolve_threat(request, threat_id):
    """mark a threat as resolved"""

    try:
        threat = ThreatEvent.objects.get(id=threat_id)
    except ThreatEvent.DoesNotExist:
        return JsonResponse({'error': 'not found'}, status=404)

    threat.is_resolved = True
    threat.save()

    return JsonResponse({'message': 'threat resolved'})
