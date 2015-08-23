# kim/pipelines/string.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from .base import (Input, Output, marshal_input_pipe, marshal_output_pipe,
                   serialize_input_pipe, serialize_output_pipe)


def is_list(field, data):
    """pipe used to determine if a value can be iterated.

    :param field: instance of :py:class:``~.Field`` being pipelined
    :param data: data being piplined for the instance of the field.
    """

    if not isinstance(data, list):
        raise field.invalid("invalid type")


def run_collection(collection_field, data, func):

    for datum in data:
        _output = {}
        func(datum, _output)
        yield _output[collection_field.name]


def marshall_collection(field, data):
    """iterate over each item in ``data`` and marshal the item through the
    wrapped field defined for this collection

    """
    wrapped_field = field.opts.field
    output = [o for o in run_collection(field, data, wrapped_field.marshal)]

    return output


def serialize_collection(field, data):
    """iterate over each item in ``data`` and serialize the item through the
    wrapped field defined for this collection

    """
    wrapped_field = field.opts.field
    output = [o for o in run_collection(field, data, wrapped_field.serialize)]

    return output


class CollectionInput(Input):

    input_pipes = marshal_input_pipe
    validation_pipes = [
        is_list,
    ]
    process_pipes = [
        marshall_collection,
    ]
    output_pipes = marshal_output_pipe


class CollectionOutput(Output):

    input_pipes = serialize_input_pipe
    validation_pipes = [
        is_list,
    ]
    process_pipes = [
        serialize_collection,
    ]
    output_pipes = serialize_output_pipe