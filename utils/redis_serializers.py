from django.core import serializers
from utils.json_encoder import JSONEncoder


class DjangoModelSerializer:

    @classmethod
    def serialize(cls, instance):
        # Django's serializers need one QuerySet or list type data to serialize in deafult
        # so need to add [] for instance into list
        return serializers.serialize('json', [instance], cls=JSONEncoder)

    @classmethod
    def deserialize(cls, serialized_data):
        # need to add .object to get original model type's object data，or not a
        # ORM's object，instead, a DeserializedObject type
        return list(serializers.deserialize('json', serialized_data))[0].object