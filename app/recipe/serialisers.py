"""Serialisers for recipe API."""
from rest_framework import serializers
from core.models import Recipe


class RecipeSerialiser(serializers.ModelSerializer):
    """Serialiser for recipe objects."""

    class Meta:
        model = Recipe
        fields = ['id', 'user','title', 'time_minutes', 'price', 'link']
        read_only_fields = ['id', 'user']

    def validate(self, attrs):
        """Validate and raise validation error if readonly fields during an update."""
        if self.instance:
            for field_name in self.initial_data:
                field = self.get_fields().get(field_name)
                if field and field.read_only:
                    raise serializers.ValidationError(
                        {field_name: 'This field is read-only.'}
                    )
        return super().validate(attrs)

class RecipeDetailSerialiser(RecipeSerialiser):
    """Serialiser for recipe detail view."""
    class Meta(RecipeSerialiser.Meta):
        fields = RecipeSerialiser.Meta.fields + ['description']