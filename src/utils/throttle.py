from rest_framework.throttling import SimpleRateThrottle, UserRateThrottle

class BaseThrottle(SimpleRateThrottle):
    """  Only throttle unauthenticated requests """

    def get_ident(self, request):
        xci = request.META.get('X-Client-IP', None)
        return xci

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            return None

        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }

class UserExistThrottle(BaseThrottle):
    scope = "user-exist"

class SendOTPThrottle(BaseThrottle):
    scope = 'send-otp'

class CheckOTPThrottle(BaseThrottle):
    scope = 'check-otp'


class IsReadThrottle(UserRateThrottle):
    scope = 'user-is-read'