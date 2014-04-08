#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import re
from datetime import date, datetime
from iso8601.iso8601 import Utc

from kim.roles import Role
from kim.mapping import Mapping
from kim.exceptions import ValidationError
from kim.types import (Nested, String, Collection, Integer, BaseType,
    TypedType, Date, DateTime, Regexp, Email)
from kim.type_mapper import TypeMapper


class BaseTypeTests(unittest.TestCase):

    def test_marshal_value(self):

        my_type = BaseType()
        self.assertEqual(my_type.marshal_value('foo'), 'foo')

    def test_serialize_value(self):

        my_type = BaseType()
        self.assertEqual(my_type.serialize_value('foo'), 'foo')

    def test_validate(self):

        my_type = BaseType()
        self.assertTrue(my_type.validate('foo'), True)


class TypedTypeTests(unittest.TestCase):

    def test_validate_requires_valid(self):
        class MyType(TypedType):

            type_ = list

        my_type = MyType()
        with self.assertRaises(ValidationError):
            self.assertTrue(my_type.validate(''))

    def test_validate(self):

        class MyType(TypedType):

            type_ = list

        self.assertTrue(MyType().validate([]))


class StringTypeTests(unittest.TestCase):

    def test_validate_requires_valid_string_type(self):

        my_type = String()
        with self.assertRaises(ValidationError):
            my_type.validate(0)

    def test_validate_string_type(self):

        my_type = String()
        my_type.validate(u'foo')


class IntegerTypeTests(unittest.TestCase):

    def test_validate_requires_valid_string_type(self):

        my_type = Integer()
        with self.assertRaises(ValidationError):
            my_type.validate('')

    def test_validate_string_type(self):

        my_type = Integer()
        my_type.validate(1)


class CollectionTypeTests(unittest.TestCase):

    def test_marshal_value(self):

        c = Collection(Integer())
        self.assertEqual(c.marshal_value([1, 2, 3]), [1, 2, 3])

    def test_serialize_value(self):

        c = Collection(Integer())
        self.assertEqual(c.serialize_value([1, 2, 3]), [1, 2, 3])

    def test_validate_iterates_type(self):

        c = Collection(Integer())
        with self.assertRaises(ValidationError):
            c.validate([1, '2', 3])

    def test_collection_requires_list_type(self):

        c = Collection(Integer())
        with self.assertRaises(ValidationError):
            c.validate('foo')

    def test_collection_requires_valid_inner_type(self):

        with self.assertRaises(TypeError):
            Collection(object())


class NestedTypeTests(unittest.TestCase):

    def test_nested_requires_valid_mapping_type(self):

        with self.assertRaises(TypeError):
            Nested(mapped=list())

    def test_nested_type_sets_role(self):

        role = Role('foo')
        mapping = Mapping()
        nested = Nested(mapped=mapping, role=role)
        self.assertEqual(nested.role, role)

    def test_nested_type_with_core_mapping_type(self):

        mapping = Mapping()
        nested = Nested(mapped=mapping)
        self.assertEqual(nested.mapping, mapping)

    def test_set_new_mapping_on_nested_type(self):

        mapping = Mapping()
        new_mapping = Mapping()

        nested = Nested(mapped=mapping)
        nested.mapping = new_mapping
        self.assertEqual(nested.mapping, new_mapping)

    def test_get_mapping_with_no_role(self):

        mapping = Mapping()
        nested = Nested(mapped=mapping)
        self.assertEqual(nested.get_mapping(), mapping)

    def test_get_mapping_with_role_set(self):

        name, email = TypeMapper('email', String()), TypeMapper('name', String())

        role = Role('foo', 'name')
        mapping = Mapping(name, email)
        nested = Nested(mapped=mapping, role=role)

        mapped = nested.get_mapping()
        self.assertNotEqual(mapped, mapping)

    def test_marshal_value(self):

        class Inner(object):

            name = 'foo'
            email = 'bar@bar.com'

        name, email = TypeMapper('email', String()), TypeMapper('name', String())
        mapping = Mapping(name, email)

        nested = Nested(mapped=mapping)
        output = nested.marshal_value(Inner())
        exp = {
            'name': 'foo',
            'email': 'bar@bar.com'
        }
        self.assertDictEqual(output, exp)

    def test_serialize_value(self):

        class Inner(object):

            name = 'foo'
            email = 'bar@bar.com'

        name, email = TypeMapper('email', String()), TypeMapper('name', String())
        mapping = Mapping(name, email)

        nested = Nested(mapped=mapping)
        output = nested.serialize_value(Inner())
        exp = {
            'name': 'foo',
            'email': 'bar@bar.com'
        }
        self.assertDictEqual(output, exp)

    def test_serialze_value_with_role(self):

        class Inner(object):

            name = 'foo'
            email = 'bar@bar.com'

        name = TypeMapper('email', String())
        email = TypeMapper('name', String())
        mapping = Mapping(name, email)

        nested = Nested(mapped=mapping, role=Role('email_only', 'email'))
        output = nested.serialize_value(Inner())
        exp = {
            'email': 'bar@bar.com'
        }
        self.assertDictEqual(output, exp)

    def test_marshal_value_with_role(self):

        class Inner(object):

            name = 'foo'
            email = 'bar@bar.com'

        name = TypeMapper('email', String())
        email = TypeMapper('name', String())
        mapping = Mapping(name, email)

        nested = Nested(mapped=mapping, role=Role('email_only', 'email'))
        output = nested.marshal_value(Inner())
        exp = {
            'email': 'bar@bar.com'
        }
        self.assertDictEqual(output, exp)

    def test_nested_validation_validates_mapped_fields_serialize(self):

        name = TypeMapper('email', String(), 'email_source')
        email = TypeMapper('name', String())
        mapping = Mapping(name, email)

        nested = Nested(mapped=mapping)

        output = nested.validate_for_serialize(
            {'name': 'foo', 'email_source': 'foo@bar.com'})
        self.assertTrue(output)

        run = lambda: nested.validate_for_serialize(
            {'name': 123, 'email_source': 'foo@bar.com'})
        self.assertRaises(ValidationError, run)

    def test_nested_validation_validates_mapped_fields_marshal(self):

        name = TypeMapper('email', String(), 'email_source')
        email = TypeMapper('name', String())
        mapping = Mapping(name, email)

        nested = Nested(mapped=mapping)

        output = nested.validate_for_marshal({
            'name': 'foo',
            'email': 'foo@bar.com'
        })
        self.assertTrue(output)

        run = lambda: nested.validate_for_marshal({
            'name': 123,
            'email': 'foo@bar.com'
        })
        self.assertRaises(ValidationError, run)

    def test_nested_marshal_validation_with_role(self):
        """When a field is of an invlaid type, but is not included in the
        role passed to a nested type, the field should be ignored
        """

        name = TypeMapper('email', String(), 'email_source')
        email = TypeMapper('name', String())
        mapping = Mapping(name, email)

        nested = Nested(mapped=mapping, role=Role('email_only', 'email'))

        output = nested.validate_for_marshal({
            'name': 123,
            'email': 'foo@bar.com'
        })
        self.assertTrue(output)

    def test_nested_serialize_validaton_with_role(self):
        """When a field is of an invlaid type, but is not included in the
        role passed to a nested type, the field should be ignored
        """

        name = TypeMapper('email', String())
        email = TypeMapper('name', String())
        mapping = Mapping(name, email)

        nested = Nested(mapped=mapping, role=Role('email_only', 'email'))

        output = nested.validate_for_serialize({
            'name': 123,
            'email': 'foo@bar.com'
        })
        self.assertTrue(output)


class DateTypeTests(unittest.TestCase):

    def test_validate_for_marshal_wrong_type(self):

        my_type = Date()
        with self.assertRaises(ValidationError):
            my_type.validate(0)

    def test_validate_for_serialize_wrong_type(self):

        my_type = Date()
        with self.assertRaises(ValidationError):
            my_type.validate(0)

    def test_validate_for_marhsal_wrong_format(self):

        my_type = Date()
        with self.assertRaises(ValidationError):
            my_type.validate_for_marshal('2014-04-ASDFSD')

    def test_validate_for_serialize_valid(self):

        my_type = Date()
        self.assertTrue(my_type.validate_for_serialize(date(2014, 4, 7)))

    def test_validate_for_marshal_valid(self):

        my_type = Date()
        self.assertTrue(my_type.validate_for_marshal('2014-04-07'))

    def test_serialize(self):
        value = date(2014, 4, 7)
        my_type = Date()
        result = my_type.serialize_value(value)

        self.assertEqual(result, '2014-04-07')

    def test_marshal(self):
        value = '2014-04-07'

        my_type = Date()
        result = my_type.marshal_value(value)

        self.assertEqual(result, date(2014, 4, 7))


class DateTimeTypeTests(unittest.TestCase):

    def test_validate_for_marshal_wrong_type(self):

        my_type = DateTime()
        with self.assertRaises(ValidationError):
            my_type.validate(0)

    def test_validate_for_serialize_wrong_type(self):

        my_type = DateTime()
        with self.assertRaises(ValidationError):
            my_type.validate(0)

    def test_validate_for_marhsal_wrong_format(self):

        my_type = DateTime()
        with self.assertRaises(ValidationError):
            my_type.validate_for_marshal('2014-04-ASDFSD')

    def test_validate_for_serialize_valid(self):

        my_type = DateTime()
        self.assertTrue(my_type.validate_for_serialize(datetime(2014, 4, 7, 5, 6, 5)))

    def test_validate_for_marshal_valid(self):

        my_type = DateTime()
        self.assertTrue(my_type.validate_for_marshal('2014-04-07T05:06:05+00:00'))

    def test_serialize(self):
        value = datetime(2014, 4, 7, 5, 6, 5, tzinfo=Utc())
        my_type = DateTime()
        result = my_type.serialize_value(value)

        self.assertEqual(result, '2014-04-07T05:06:05+00:00')

    def test_marshal(self):
        value = '2014-04-07T05:06:05+00:00'

        my_type = DateTime()
        result = my_type.marshal_value(value)

        self.assertEqual(result, datetime(2014, 4, 7, 5, 6, 5, tzinfo=Utc()))


class RegexpTypeTests(unittest.TestCase):
    def test_validate_no_match(self):

        my_type = Regexp(pattern=re.compile('[0-9]+'))
        with self.assertRaises(ValidationError):
            my_type.validate('hello')

    def test_validate_valid(self):

        my_type = Regexp(pattern=re.compile('[0-9]+'))
        self.assertTrue(my_type.validate('1234'))


class EmailTypeTests(unittest.TestCase):
    def test_validate_no_match(self):

        my_type = Email()
        with self.assertRaises(ValidationError):
            my_type.validate('hello')

    def test_validate_valid(self):

        my_type = Email()
        self.assertTrue(my_type.validate('jack@gmail.com'))
