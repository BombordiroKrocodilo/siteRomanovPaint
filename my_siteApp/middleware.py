from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from django.contrib.auth.models import AnonymousUser

class JWTAuthenticationMiddleware(MiddlewareMixin):
    
    def process_request(self, request):
        if request.path.startswith('/admin/') or \
            request.path.startswith('/static/') or \
            request.path.startswith('/media/'):
            return None
        
        if request.path.startswith('/api/'):
            try:
                jwt_auth = JWTAuthentication()
                auth_result = jwt_auth.authenticate(request)
                
                if auth_result is not None:
                    user, token = auth_result
                    request.user = user
                    request.jwt_token = token
                else:
                    request.user = AnonymousUser()
            except (InvalidToken, AuthenticationFailed) as e:
                request.user = AnonymousUser()
        
        return None

    def process_exception(self, request, exception):
        """Обработка исключений JWT аутентификации"""
        if isinstance(exception, (InvalidToken, AuthenticationFailed)):
            return JsonResponse({
                'error': 'Неверный или просроченный токен',
                'detail': str(exception)
            }, status=401)
        return None