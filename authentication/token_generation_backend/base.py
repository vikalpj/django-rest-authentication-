# -*- coding: utf-8 -*-


class BaseBackend(object):
    def get_token_for_user(self, user, *args, **kwargs):
        """
        Generate a new signed token containing
        a specified user.
        """
        raise NotImplemented()

    def get_user_for_token(self, token, *args, **kwargs):
        """
        Given a self-contained token and a scope try to parse and
        unsign it.

        If token passes a validation, returns
        a user instance corresponding with session_id stored
        in the incoming token.
        """
        raise NotImplemented()
