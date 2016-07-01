# # -*- coding: utf-8 -*-

# Third Party Stuff
from django.conf import settings
from django.utils.module_loading import import_string

TOKEN_BACKEND_SERVICE_CLASS = import_string(settings.TOKEN_BACKEND_SERVICE)


def get_user_for_token(token, *args, **kwargs):
    return TOKEN_BACKEND_SERVICE_CLASS().get_user_for_token(token, *args, **kwargs)


def get_token_for_user(user, *args, **kwargs):
    return TOKEN_BACKEND_SERVICE_CLASS().get_token_for_user(user, *args, **kwargs)
