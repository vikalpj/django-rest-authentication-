# -*- coding: utf-8 -*-

# Third Party Stuff
import pytest
from django.contrib.auth import get_user_model
from django_dynamic_fixture import G


User = get_user_model()


@pytest.fixture
def user(*args, **kwagrs):
    user_obj = G(User, **kwagrs)
    return user_obj
