from django.core import serializers
from utils.json_encoder import JSONEncoder


class DjangoModelSerializer:

    @classmethod
    def serialize(cls, instance):
        # Django serializers need a default QuerySet or list to serialize
        # so instance need to add [] so that it converted to list
        return serializers.serialize('json', [instance], cls=JSONEncoder)

    @classmethod
    def deserialize(cls, serialized_data):
        # .object to get original Model object
        # otherwise it's DeserializedObject not ORM object
        return list(serializers.deserialize('json', serialized_data))[0].object