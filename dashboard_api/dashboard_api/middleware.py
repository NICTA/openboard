#   Copyright 2015 NICTA
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

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

