from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from djoser.views import UserViewSet
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import RecipeFilter, IngredientFilter
from .permissions import IsOwnerOrAdminOrReadOnly
from .serializers import (RecipeSerializer,
                          CustomUserSerializer, IngredientSerializer,
                          TagSerializer, FollowSerializer, FolloweeSerializer,
                          BookmarkSerializer, ShoppingListSerializer)

from .models import (Ingredient, Recipe, Tag, Follow, Bookmark, ShoppingList)
from .mixins import CustomCreateDeleteObjSerializerMixin

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsOwnerOrAdminOrReadOnly]

    @action(
        detail=True, methods=['post'], permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        follower = request.user
        followee = get_object_or_404(User, id=id)

        data = {
            'follower': follower.id,
            'followee': followee.id
        }

        serializer = FollowSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        follow = get_object_or_404(
            Follow,
            followee_id=id,
            follower_id=request.user.id
        )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        queryset = Follow.objects.filter(follower=request.user)
        page = self.paginate_queryset(queryset)
        serializer = FolloweeSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class RecipeViewSet(
                    viewsets.ModelViewSet,
                    CustomCreateDeleteObjSerializerMixin
):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_class = RecipeFilter
    permission_classes = [IsOwnerOrAdminOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True, methods=['post'], permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        return self.create_obj(BookmarkSerializer, request, pk)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        return self.delete_obj(Bookmark, pk)

    @action(
        detail=True, methods=['post'], permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        return self.create_obj(ShoppingListSerializer, request, pk)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        return self.delete_obj(ShoppingList, pk)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = (Ingredient.objects
                       .select_related('recipe_ingredients')
                       .filter(recipes__shopping_list__user=request.user)
                       .values('name', 'measurement_unit')
                       .annotate(amount=Sum('recipe_ingredients__amount'))
                       )
        shopping_list = []
        for ingredient in ingredients:
            shopping_list += [
                f"{ingredient['name']} "
                f"({ingredient['measurement_unit']}) — "
                f"{ingredient['amount']}"
            ]

        response = HttpResponse(
            '\n'.join(shopping_list),
            content_type='text/plain',
            status=status.HTTP_200_OK)
        response['Content-Disposition'] = 'attachment; filename="shoplist.txt"'

        return response


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_class = IngredientFilter
    pagination_class = None
    permission_classes = [IsOwnerOrAdminOrReadOnly]


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [IsOwnerOrAdminOrReadOnly]
