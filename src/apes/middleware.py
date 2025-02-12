"""

User-defined middleware for the APES project.

"""

from django.shortcuts import render
from django.db.utils import OperationalError, DatabaseError
from django.utils.deprecation import MiddlewareMixin

class DatabaseErrorMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if isinstance(exception, (OperationalError, DatabaseError)):
            return render(request, 'database_error.html', {'error': f"Timeout: Database connection failed.\n Error found:{exception}"}, status=500)