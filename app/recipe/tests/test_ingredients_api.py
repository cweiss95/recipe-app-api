"""
Tests for the ingredients API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serialisers import IngredientSerialiser

INGREDIENTS_URL = reverse('recipe:ingredient-list')


def detail_url(ingredient_id):
    """Return ingredient detail URL."""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_user(email='test@example.com', password='testpass123'):
    """Helper function to create and return a user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicIngredientsApiTests(TestCase):
    """Test unauthenticated API access."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required."""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test authenticated API access."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving ingredients."""
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerialiser(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that ingredients returned are for the authenticated user."""
        other_user = create_user(
            email='other@example.com',
            password='testpass123')
        Ingredient.objects.create(
            user=other_user,
            name='Vinegar')
        ingredient = Ingredient.objects.create(user=self.user, name='Pepper')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_update_ingredient_error_on_read_only_fields(self):
        """Test that updating an ingredient
        with read-only fields raises an error."""
        ingredient = Ingredient.objects.create(user=self.user, name='Sugar')
        payload = {
            'name': 'Brown Sugar',
            'user': create_user(
                email='other@example.com',
                password='testpass123')
        }
        res = self.client.patch(detail_url(ingredient.id), payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_ingredient(self):
        """Test updating an ingredient."""
        ingredient = Ingredient.objects.create(user=self.user, name='Sugar')
        payload = {'name': 'Brown Sugar'}
        res = self.client.patch(detail_url(ingredient.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])
        self.assertEqual(ingredient.user, self.user)

    def test_delete_ingredient(self):
        """Test deleting an ingredient."""
        ingredient = Ingredient.objects.create(user=self.user, name='Sugar')
        res = self.client.delete(detail_url(ingredient.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredient.objects.filter(id=ingredient.id).exists())

    def test_delete_ingredient_other_user(self):
        """Test that deleting another user's ingredient fails."""
        other_user = create_user(
            email='other@example.com',
            password='testpass123')
        ingredient = Ingredient.objects.create(user=other_user, name='Sugar')
        res = self.client.delete(detail_url(ingredient.id))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Ingredient.objects.filter(id=ingredient.id).exists())
