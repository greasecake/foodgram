import django_filters as filters
from rest_framework import serializers

from .models import Recipe, Ingredient


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
    )
    author = filters.ModelChoiceFilter(
        queryset=Recipe.objects.all()
    )
    is_favorited = filters.CharFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.CharFilter(
        method='filter_is_in_shopping_cart'
    )

    def filter_is_favorited(self, queryset, name, value):
        if value == '1':
            return queryset.filter(bookmarks__user=self.request.user)
        elif value == '0':
            return queryset.filter(bookmarks__user__isnull=True)
        else:
            raise serializers.ValidationError(
                'Недопустимое значение параметра is_favorited'
            )

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value == '1':
            return queryset.filter(shopping_list__user=self.request.user)
        elif value == '0':
            return queryset.filter(shopping_list__user__isnull=True)
        else:
            raise serializers.ValidationError(
                'Недопустимое значение параметра is_in_shopping_cart'
            )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart',)


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
