# Zero Trust API Gateway — Security Dashboard

A Django-based security monitoring dashboard that provides real-time visibility into your API traffic, threat detection, and IP management.

## Features

- **Real-time Dashboard** — Monitor requests, blocked IPs, rate violations, and threats at a glance
- **Traffic Charts** — Visualize request patterns over the last 24 hours
- **IP Blocking** — Block/unblock IPs directly from the dashboard
- **Rate Limiting** — Configurable per-IP rate limits with auto-blocking for repeat offenders
- **Anomaly Detection** — Detects path scanning (recon) and brute force login attempts
- **Request Logging** — Full request log with method, path, status, IP, and user agent
- **JWT Authentication** — Token-based auth with access + refresh tokens
- **Threat Feed** — Live feed of security events with severity levels

## Security Pipeline

```
Client → IP Blocker → Rate Limiter → JWT Auth → Request Logger → Anomaly Detector → Your App
```

## Quick Start

```bash
# clone and setup
git clone git@github.com:paul-raja-dev/zero-trust.git
cd zero-trust
python -m venv venv
source venv/bin/activate
pip install -r requirments.txt

# run migrations
python manage.py migrate

# create admin user
python manage.py createsuperuser

# start the server
python manage.py runserver
```

Then open `http://localhost:8000/` to see the dashboard.

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Security dashboard UI |
| `/api/stats/` | GET | Overview statistics |
| `/api/requests/` | GET | Paginated request logs |
| `/api/threats/` | GET | Recent threat events |
| `/api/traffic/` | GET | Hourly traffic data |
| `/api/top-ips/` | GET | Top IPs by request count |
| `/api/blocked-ips/` | GET | List blocked IPs |
| `/api/block-ip/` | POST | Block an IP |
| `/api/unblock-ip/<id>/` | POST | Unblock an IP |
| `/api/login/` | POST | JWT login |
| `/api/refresh/` | POST | Refresh JWT token |

## Configuration

Add these to `settings.py` to customize:

```python
ZTG_RATE_LIMIT = 30        # max requests per window
ZTG_RATE_WINDOW = 60       # window size in seconds
ZTG_AUTO_BLOCK_AFTER = 5   # auto-block after N violations
```

## Tech Stack

- Django 6.0
- Django REST Framework
- Chart.js (CDN)
- SQLite
- PyJWT