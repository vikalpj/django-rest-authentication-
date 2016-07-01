# -*- coding: utf-8 -*-
"""
Authentication backends for rest framework.

This module exposes two backends: session and token.

The first (session) is a modified version of standard
session authentication backend of restframework with
csrf token disabled.

And the second (token) implements own version of oauth2
like authentiacation but with selfcontained tokens. Thats
makes authentication totally stateles.

It uses django signing framework for create new
selfcontained tokens. This trust tokes from external
fraudulent modifications.
"""

# Standard Library
import re

# Third Party Stuff
from rest_framework.authentication import BaseAuthentication

# bcc Stuff
from bcc.base import exceptions as exc

from .services import get_user_for_token


class SessionAuthentication(BaseAuthentication):
    """
    Session based authentication like the standard
    `rest_framework.authentication.SessionAuthentication`
    but with csrf disabled (for obvious reasons because
    it is for api).

    NOTE: this is only for api web interface. Is not used
    for common api usage and should be disabled on production.
    """

    def authenticate(self, request):
        http_request = request._request
        user = getattr(http_request, 'user', None)

        if not user or not user.is_active:
            return None

        return (user, None)


class TokenAuthentication(BaseAuthentication):
    """
    Self-contained stateless authentication implementatrion
    that work similar to oauth2.
    It uses json web tokens (https://github.com/jpadilla/pyjwt) for trust
    data stored in the token.
    """

    auth_rx = re.compile(r"^Token (.+)$")

    def authenticate(self, request):
        if "HTTP_AUTHORIZATION" not in request.META:
            return None

        token_rx_match = self.auth_rx.search(
            request.META["HTTP_AUTHORIZATION"])
        if not token_rx_match:
            return None

        token = token_rx_match.group(1)

        user = self.get_user(token, request)
        # Pass request object to save the session object in request
        user = get_user_for_token(token, request)
        if not user:
            raise exc.NotAuthenticated("Invalid request. Please retry.")

        return (user, token)

    def get_user(self, token, *args, **kwargs):
        return get_user_for_token(token)

    def authenticate_header(self, request):
        return 'Token realm="api"'


class SessionTokenAuthentication(TokenAuthentication):
    """
    Self-contained stateless authentication implementatrion
    that work similar to oauth2.
    It uses django sessions as the tokens. to seamlessly integrate
    with django login/logout implementations
    """
    def get_user(self, token, request, *args, **kwargs):
        return get_user_for_token(token, request)
