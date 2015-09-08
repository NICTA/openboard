from django.contrib.sessions.middleware import SessionMiddleware

class APISessionMiddleware(SessionMiddleware):
    def process_request(self, request):
        session_header = request.META.get("HTTP_X_DASHBOARD_SESSION_ID")
        if session_header:
            request.session = self.SessionStore(session_header)
        else:
            super(APISessionMiddleware, self).process_request(request)

    def process_response(self, request, response):
        refreshed_response = super(APISessionMiddleware, self).process_response(request, response)
        if request.META.get("HTTP_X_DASHBOARD_SESSION_ID"):
            response["X-Dashboard-Session-Id"] = response.session.session_key
        return refreshed_response

