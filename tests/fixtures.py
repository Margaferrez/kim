from kim import field
from kim.mapper import PolymorphicMapper


class TestType(object):
    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class IterableTestType(object):
    """This test type mimics constructs like SQA's result class or
    declarative_base objects that support iteration that enables access to
    attributes.
    """
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        for k, v in kwargs.items():
            setattr(self, k, v)

    def keys(self):
        return self.kwargs.keys()


class TestField(field.Field):
    pass


class SchedulableMapper(PolymorphicMapper):

    __type__ = TestType
    id = field.Integer(read_only=True)
    name = field.String()
    object_type = field.String(choices=['event', 'task'])

    __mapper_args__ = {
        'polymorphic_on': object_type,
        'allow_polymorphic_marshal': True,
    }

    __roles__ = {
        'name_only': ['name'],
    }


class EventMapper(SchedulableMapper):

    __type__ = TestType
    location = field.String()

    __mapper_args__ = {
        'polymorphic_name': 'event'
    }


class TaskMapper(SchedulableMapper):

    __type__ = TestType
    status = field.String()

    __mapper_args__ = {
        'polymorphic_name': 'task'
    }
