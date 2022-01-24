from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from .models import Recipe
from .serializers import RecipeMinifiedSerializer


class CustomCreateDeleteObjSerializerMixin:
    def delete_obj(self, model, pk):
        obj = get_object_or_404(model, recipe_id=pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create_obj(self, serializer, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
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
