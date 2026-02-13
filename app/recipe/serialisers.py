"""Serialisers for recipe API."""
from rest_framework import serializers
from core.models import Recipe, Tag, Ingredient


def validate_read_only_fields(serialiser):
    """Validate and raise validation error if
       readonly fields during an update."""
    if serialiser.instance:
        for field_name in serialiser.initial_data:
            field = serialiser.get_fields().get(field_name)
            if field and field.read_only:
                raise serializers.ValidationError(
                    {field_name: 'This field is read-only.'}
                )


class IngredientSerialiser(serializers.ModelSerializer):
    """Serialiser for ingredient objects."""

    class Meta:
        model = Ingredient
        fields = ['id', 'user', 'name']
        read_only_fields = ['id', 'user']

    def validate(self, attrs):
        """Validate and raise validation error if
           readonly fields during an update."""
        validate_read_only_fields(self)
        return super().validate(attrs)


class TagSerialiser(serializers.ModelSerializer):
    """Serialiser for tag objects."""

    class Meta:
        model = Tag
        fields = ['id', 'user', 'name']
        read_only_fields = ['id', 'user']

    def validate(self, attrs):
        """Validate and raise validation error if
           readonly fields during an update."""
        validate_read_only_fields(self)
        return super().validate(attrs)


class RecipeSerialiser(serializers.ModelSerializer):
    """Serialiser for recipe objects."""
    tags = TagSerialiser(many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            'id', 'user', 'title', 'time_minutes',
            'price', 'link', 'tags']
        read_only_fields = ['id', 'user']

    def get_or_create_tags(self, tags_data, recipe):
        """Handle getting or creating tags as needed."""
        auth_user = self.context['request'].user
        for tag in tags_data:
            tag_obj, created = Tag.objects.get_or_create(user=auth_user, **tag)
            recipe.tags.add(tag_obj)

    def validate(self, attrs):
        """Validate and raise validation error if
           readonly fields during an update."""
        validate_read_only_fields(self)
        return super().validate(attrs)

    def create(self, validated_data):
        """Create a recipe."""
        tags_data = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)
        self.get_or_create_tags(tags_data, recipe)

        return recipe

    def update(self, instance, validated_data):
        """Update recipe."""
        tags_data = validated_data.pop('tags', None)
        if tags_data is not None:
            instance.tags.clear()
            self.get_or_create_tags(tags_data, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class RecipeDetailSerialiser(RecipeSerialiser):
    """Serialiser for recipe detail view."""
    class Meta(RecipeSerialiser.Meta):
        fields = RecipeSerialiser.Meta.fields + ['description']
