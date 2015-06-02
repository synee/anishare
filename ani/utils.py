# -*- coding: utf-8 -*-

from .auth import current_user


def get_namespace(**kwargs):
    import humanize
    kwargs.update({
        'humanize': humanize,
        'current_user': current_user()
    })
    return kwargs
