"""
Views for recipe APIs.
"""
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag, Ingredient

from recipe import serialisers


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serialisers.RecipeDetailSerialiser
    queryset = Recipe.objects.all()

    def get_queryset(self):
        """Return objects for the current authenticated user only."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'list':
            return serialisers.RecipeSerialiser

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)


class BaseRecipeAttrViewSet(mixins.ListModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin,
                            viewsets.GenericViewSet):
    """Base viewset for user owned recipe attributes."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return objects for the current authenticated user only."""
        return self.queryset.filter(user=self.request.user).order_by('-name')


class TagViewSet(BaseRecipeAttrViewSet):
    """View for manage tag APIs."""
    serializer_class = serialisers.TagSerialiser
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """View for manage ingredient APIs."""
    serializer_class = serialisers.IngredientSerialiser
    queryset = Ingredient.objects.all()
