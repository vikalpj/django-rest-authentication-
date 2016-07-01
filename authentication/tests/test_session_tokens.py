# -*- coding: utf-8 -*-

# Standard Library
from importlib import import_module

# Third Party Stuff
from authentication.token_generation_backend.session_tokens import SessionToken
from django.conf import settings

from .fixtures import *  # noqa

session_engine = import_module(settings.SESSION_ENGINE)

SessionStore = session_engine.SessionStore

pytestmark = pytest.mark.django_db


class MockedRequest:
    def __init__(self, session):
        self.session = session


def test_get_token_for_user(user):
    request = MockedRequest(SessionStore())
    session_token = SessionToken()
    session_key = session_token.get_token_for_user(user, request)

    # check this session key refers to a session with the above user
    session_object = SessionStore(session_key)
    assert session_object[SessionToken.SESSION_USER_ID] == str(user.id)
    assert session_object[SessionToken.SESSION_USER_HASH] == user.get_session_auth_hash()


def test_user_for_token(user):
    session = SessionStore()
    session[SessionToken.SESSION_USER_ID] = str(user.id)
    session[SessionToken.SESSION_USER_HASH] = user.get_session_auth_hash()
    session.save()
    request = MockedRequest(session)
    session_token = SessionToken()

    returned_user = session_token.get_user_for_token(session.session_key, request)

    # check user returned is the correct user
    assert str(returned_user.id) == str(user.id)
