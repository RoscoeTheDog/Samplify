from __future__ import absolute_import, division, print_function

import datetime
import json
import operator
import sys
import time

import six

from structlog._frames import (
    _find_first_app_frame_and_name,
    _format_exception,
    _format_stack,
)

def add_structlog_level(logger, name, event_dict):

    event_dict['level'] = name.lower()

    return event_dict


def order_keys(logger, name, event_dict):
    keys = ['timestamp', 'level', 'event', 'msg', 'path', 'exception', 'exc_info', 'path']

    # if keys is None:
    #     return event_dict
    # else:
    _ordered_keys = keys
    _event_dict = event_dict.copy()

    event_dict = {}

    for key in _ordered_keys:

        if _event_dict:
            for k, v in list(_event_dict.items()):
                if key == k:
                    event_dict[key] = _event_dict.pop(k)
                else:
                    continue

    return event_dict

class OrderKeys(object):

    def __new__(cls, keys=None):
        _temp = ['timestamp', 'level', 'event', 'msg', 'exc_info', 'path']

        if keys is None:

            def organizer(self, logger, name, event_dict):
                return event_dict
        else:
            def organizer(self, logger, name, event_dict):
                _ordered_keys = keys
                _event_dict = event_dict.copy()

                event_dict = {}

                for key in _ordered_keys:

                    if _event_dict:
                        for k, v in list(_event_dict.items()):
                            if key == k:
                                event_dict[key] = _event_dict.pop(k)

                return event_dict

        return type("OrderKeys", (object,), {"__call__": organizer})()