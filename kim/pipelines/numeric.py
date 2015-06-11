# kim/pipelines/numeric.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from .base import Input, Output, get_data_from_source


def is_valid_integer(field, data):
    """pipe used to determine if a value can be coerced to an int

    :param field: instance of :py:class:``~.Field`` being pipelined
    :param data: data being piplined for the instance of the field.
    """

    try:
        return int(data)
    except ValueError:
        raise field.invalid("field is not a valid integer")


class IntegerInput(Input):

    pipes = [
        get_data_from_source,
        is_valid_integer
    ]


class IntegerOutput(Output):

    pipes = [
        get_data_from_source,
    ]
