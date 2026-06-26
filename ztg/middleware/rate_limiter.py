from django.http import JsonResponse
from ztg.models import RateLimitViolation, ThreatEvent, BlockedIP
from django.conf import settings
import time


class RateLimiter:

    request_counts = {}

    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit = getattr(settings, 'ZTG_RATE_LIMIT', 100)
        self.window_size = getattr(settings, 'ZTG_RATE_WINDOW', 60)
        self.auto_block_threshold = getattr(settings, 'ZTG_AUTO_BLOCK_AFTER', 10)

    # paths that should never be rate limited
    exempt_paths = ['/admin', '/static', '/api/', '/']

    def __call__(self, request):

        for path in self.exempt_paths:
            if request.path.startswith(path):
                return self.get_response(request)

        ip_addr = request.META.get('REMOTE_ADDR')
        current_time = time.time()

        # get timestamps for this ip, add current one
        timestamps = self.request_counts.get(ip_addr, [])
        timestamps.append(current_time)

        # keep only timestamps within the window
        timestamps = [t for t in timestamps if t > current_time - self.window_size]
        self.request_counts[ip_addr] = timestamps

        if len(timestamps) > self.rate_limit:

            # log the violation to db
            RateLimitViolation.objects.create(
                ip_address=ip_addr,
                path=request.path
            )

            # count how many violations this ip has recently
            recent_violations = RateLimitViolation.objects.filter(
                ip_address=ip_addr
            ).count()

            # auto-block if they keep abusing
            if recent_violations >= self.auto_block_threshold:
                BlockedIP.objects.get_or_create(
                    ip_address=ip_addr,
                    defaults={'reason': f'Auto-blocked: {recent_violations} rate limit violations'}
                )
                ThreatEvent.objects.create(
                    threat_type='rate_abuse',
                    severity='high',
                    ip_address=ip_addr,
                    description=f'Auto-blocked after {recent_violations} rate limit violations'
                )

            return JsonResponse({'error': 'Too many requests'}, status=429)

        response = self.get_response(request)
        return response