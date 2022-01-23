from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from .models import Tag, RecipeIngredient
from .serializers import RecipeMinifiedSerializer


class CustomCreateDeleteObjSerializerMixin:
    def delete_obj(self, model, pk):
        obj = get_object_or_404(model, recipe_id=pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create_obj(self, serializer, request, pk):
        recipe = get_object_or_404(serializer, id=pk)
        data = {
            'user': request.user.id,
            'recipe': recipe.id
        }
        serializer = serializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            RecipeMinifiedSerializer(recipe).data,
            status=status.HTTP_201_CREATED
        )


def recipe_add_tag_ingredient(recipe, tag_ids, ingredients):
    if tag_ids:
        recipe.tags = set()
        for tag_id in tag_ids:
            recipe.tags.add(get_object_or_404(Tag, id=tag_id))

    for ingredient in ingredients:
        RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient_id=ingredient.get('id'),
            amount=ingredient.get('amount')
        )
