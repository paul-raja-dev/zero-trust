from ztg.services.anomaly_detector import AnomalyDetector


class AnomalyMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        self.detector = AnomalyDetector()

    def __call__(self, request):

        if request.path.startswith('/admin') or request.path.startswith('/static'):
            return self.get_response(request)

        response = self.get_response(request)

        # run anomaly checks after we have the response (need status code)
        try:
            self.detector.check_all(request, response)
        except Exception:
            pass  # never let anomaly detection break actual requests

        return response
