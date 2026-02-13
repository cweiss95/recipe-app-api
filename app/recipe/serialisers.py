"""Serialisers for recipe API."""
from rest_framework import serializers
from core.models import Recipe, Tag


class TagSerialiser(serializers.ModelSerializer):
    """Serialiser for tag objects."""

    class Meta:
        model = Tag
        fields = ['id', 'user', 'name']
        read_only_fields = ['id', 'user']

    def validate(self, attrs):
        """Validate and raise validation error if
           readonly fields during an update."""
        if self.instance:
            for field_name in self.initial_data:
                field = self.get_fields().get(field_name)
                if field and field.read_only:
                    raise serializers.ValidationError(
                        {field_name: 'This field is read-only.'}
                    )
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

    def validate(self, attrs):
        """Validate and raise validation error if
           readonly fields during an update."""
        if self.instance:
            for field_name in self.initial_data:
                field = self.get_fields().get(field_name)
                if field and field.read_only:
                    raise serializers.ValidationError(
                        {field_name: 'This field is read-only.'}
                    )
        return super().validate(attrs)

    def create(self, validated_data):
        """Create a recipe."""
        tags_data = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)
        auth_user = self.context['request'].user
        for tag in tags_data:
            tag_obj, created = Tag.objects.get_or_create(user=auth_user, **tag)
            recipe.tags.add(tag_obj)

        return recipe


class RecipeDetailSerialiser(RecipeSerialiser):
    """Serialiser for recipe detail view."""
    class Meta(RecipeSerialiser.Meta):
        fields = RecipeSerialiser.Meta.fields + ['description']
