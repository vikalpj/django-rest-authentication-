# -*- coding: utf-8 -*-

# Standard Library
import logging
from importlib import import_module

# Third Party Stuff
from django.conf import settings
from django.contrib.auth import get_user_model

from .base import BaseBackend

user_model = get_user_model()
log = logging.getLogger(__name__)
session_engine = import_module(settings.SESSION_ENGINE)
SessionStore = session_engine.SessionStore


class SessionToken(BaseBackend):
    SESSION_USER_ID = '_auth_user_id'
    SESSION_USER_HASH = '_auth_user_hash'

    def get_user_for_token(self, session_id, request, *args, **kwargs):
        """
        Given a request object and session_id try to return the user
        object and update the session object in request.
        """
        # SessionStore initialize the session object using session_key
        session = SessionStore(session_id)

        # Save the user's session object in request.
        request.session = session

        user = None
        if self.SESSION_USER_ID in session:
            user_id = user_model._meta.pk.to_python(session[self.SESSION_USER_ID])
            try:
                user = user_model._default_manager.get(pk=user_id)
                # Check current user's hash to match stored hash.
                # If they don't match than user have changed the password.
                # Delete this session to make user login again.
                if hasattr(user, 'get_session_auth_hash'):
                    session_auth_hash = user.get_session_auth_hash()
                    if session_auth_hash != session[self.SESSION_USER_HASH]:
                        request.session.flush()
                        user = None
            except user_model.DoesNotExist:
                return None
        return user

    def get_token_for_user(self, user, request, *args, **kwargs):
        """
        Generate a new session id object
        """
        request.session[self.SESSION_USER_ID] = user._meta.pk.value_to_string(user)

        # Each user have unique hash generated using user's password.
        # Store this hash in session object to check if user's password changes
        # than delete all other user sessions.
        request.session[self.SESSION_USER_HASH] = user.get_session_auth_hash()

        # TODO: Need to set expiry system to extend expiry on each valid authentication.
        if hasattr(request, 'user'):
            request.user = user
        request.session.save()

        # Session middleware saves/update session on each modification.
        # Set modified False to avoid database query.
        request.session.modified = False
        return request.session.session_key
