from rest_framework.generics import get_object_or_404

from .models import Tag, RecipeIngredient


def recipe_add_tag_ingredient(recipe, tag_ids, ingredients):
    if tag_ids:
        for tag in recipe.tags.all():
            recipe.tags.remove(tag)
        for tag_id in tag_ids:
            recipe.tags.add(get_object_or_404(Tag, id=tag_id))

    for ingredient in ingredients:
        RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient_id=ingredient.get('id'),
            amount=ingredient.get('amount')
        )
