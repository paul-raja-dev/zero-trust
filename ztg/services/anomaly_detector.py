from django.utils import timezone
from datetime import timedelta
from django.db.models import Count

from ztg.models import RequestLog, ThreatEvent


class AnomalyDetector:
    """detects suspicious patterns in request traffic"""

    def __init__(self):
        self.spike_multiplier = 3       # 3x above average = spike
        self.scan_threshold = 10        # 10+ unique 404 paths from same ip = scanning
        self.brute_force_threshold = 5  # 5+ failed auth attempts = brute force
        self.window_minutes = 10        # look at last 10 minutes

    def check_all(self, request, response):
        """run all anomaly checks for a request"""
        ip = request.META.get('REMOTE_ADDR', '')

        self.check_path_scanning(ip)
        self.check_brute_force(ip, request.path, response.status_code)

    def check_path_scanning(self, ip):
        """detect IPs hitting many different paths that return 404 (recon/scanning)"""

        window = timezone.now() - timedelta(minutes=self.window_minutes)

        unique_404_paths = (
            RequestLog.objects
            .filter(ip_address=ip, status_code=404, timestamp__gte=window)
            .values('path')
            .distinct()
            .count()
        )

        if unique_404_paths >= self.scan_threshold:
            # only create one threat per IP per window
            already_flagged = ThreatEvent.objects.filter(
                threat_type='path_scan',
                ip_address=ip,
                timestamp__gte=window
            ).exists()

            if not already_flagged:
                ThreatEvent.objects.create(
                    threat_type='path_scan',
                    severity='high',
                    ip_address=ip,
                    description=f'IP hit {unique_404_paths} unique 404 paths in {self.window_minutes}min — possible reconnaissance'
                )

    def check_brute_force(self, ip, path, status_code):
        """detect repeated failed auth attempts from the same IP"""

        auth_paths = ['/api/login/', '/admin/login/']
        if path not in auth_paths or status_code != 401:
            return

        window = timezone.now() - timedelta(minutes=self.window_minutes)

        failed_attempts = (
            RequestLog.objects
            .filter(ip_address=ip, status_code=401, path__in=auth_paths, timestamp__gte=window)
            .count()
        )

        if failed_attempts >= self.brute_force_threshold:
            already_flagged = ThreatEvent.objects.filter(
                threat_type='brute_force',
                ip_address=ip,
                timestamp__gte=window
            ).exists()

            if not already_flagged:
                ThreatEvent.objects.create(
                    threat_type='brute_force',
                    severity='critical',
                    ip_address=ip,
                    description=f'{failed_attempts} failed login attempts in {self.window_minutes}min — possible brute force attack'
                )
