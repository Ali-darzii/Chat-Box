# your_app_name/middleware.py
import logging

from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import AnonymousUser

from channels.auth import AuthMiddlewareStack

logger = logging.getLogger('django')

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        try:
            token_key = dict(scope['headers']).get(b'authorization')
            token_key = token_key.decode('utf-8')
        except IndexError:
            token_key = None
        if token_key:
            scope['user'] = await self.get_user(token_key)
        else:
            scope['user'] = AnonymousUser()
        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user(self, token_key):
        try:
            user = JWTAuthentication().authenticate(Request(token_key))
            if user is not None:
                return user[0]
        except:
            return AnonymousUser()

class Request:
    """ Mocking request"""
    def __init__(self, token_key):
        self.META = {'HTTP_AUTHORIZATION': f'{token_key}'}


def JWTAuthMiddlewareStack(app):
    """This function wrap channels authentication stack with JWTAuthMiddleware."""
    return JWTAuthMiddleware(AuthMiddlewareStack(app))