import django_filters as filters

from .models import Recipe, Ingredient, User


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
    )
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all()
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
        if value == '0':
            return queryset.filter(bookmarks__user__isnull=True)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value == '1':
            return queryset.filter(shopping_list__user=self.request.user)
        if value == '0':
            return queryset.filter(shopping_list__user__isnull=True)

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart',)


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
