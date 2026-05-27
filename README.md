# Zero Trust API Gateway

A Django-based API gateway handling JWT validation, rate limiting,
IP whitelisting, request logging, and anomaly detection.

## Pipeline
Client → JWT → IP Whitelist → Rate Limit → Logger → Anomaly → Proxy → Backend

## Status
🔧 In progress