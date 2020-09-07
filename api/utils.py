from rest_framework.serializers import ModelSerializer
from api.models import *

class PersonModelSerializer(ModelSerializer):
	class Meta:
		model = Person
		fields = '__all__'

	def create(self, validated_data):
		instance = self.Meta.model(**validated_data)
		instance.save()

		return instance


class ContactPersonModelSerializer(ModelSerializer):
	class Meta:
		model = ContactPerson
		fields = '__all__'

	def create(self, validated_data):
		instance = self.Meta.model(**validated_data)
		instance.save()

		return instance