from django.contrib import admin
from .models import *


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'text', 'author', 'cooking_time',)
    search_fields = ('name',)
    list_filter = ('author',)
    empty_value_display = '-пусто-'
    exclude = ('ingredients',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    class Meta:
        model = Follow
        list_display = ('follower', 'followee',)


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    class Meta:
        model = Bookmark
        list_display = ('user', 'recipe',)


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    class Meta:
        model = ShoppingList
        list_display = ('user', 'recipe',)
