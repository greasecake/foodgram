from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .models import (Ingredient, Recipe, RecipeIngredient,
                     Tag, Follow, Bookmark, ShoppingList)


User = get_user_model()


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return Follow.objects.filter(
                follower=request.user, followee=obj
            ).exists()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients', many=True, read_only=True
    )
    tags = TagSerializer(many=True, read_only=True, required=False)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )
        read_only_fields = ('author',)

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Bookmark.objects.filter(
            user=request.user, recipe=obj.id
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingList.objects.filter(
            user=request.user, recipe=obj.id
        ).exists()

    def validate(self, attrs):
        print(attrs)
        ingredients = attrs.get('ingredients')
        unique_ids = set()
        for ingredient in ingredients:
            if ingredient.get('id') in unique_ids:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться'
                )
            unique_ids.add(ingredient.get('id'))
            if int(ingredient.get('amount')) <= 0:
                raise serializers.ValidationError(
                    'Количество должно быть больше 0'
                )

        tag_ids = attrs.get('tags')
        for tag_id in tag_ids:
            if not Tag.objects.filter(id=tag_id).exists():
                raise serializers.ValidationError(
                    'Указан несуществующий тег'
                )

        cooking_time = attrs.get('cooking_time')
        if cooking_time <= 0:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 0'
            )

        return attrs

    def create(self, validated_data):
        tag_ids = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for tag_id in tag_ids:
            recipe.tags.add(get_object_or_404(Tag, id=tag_id))

        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            )

        return recipe

    def update(self, instance, validated_data):
        tag_ids = validated_data.pop('tags')
        RecipeIngredient.objects.filter(recipe=instance).delete()

        if tag_ids:
            instance.tags = set()
            for tag_id in tag_ids:
                instance.tags.add(get_object_or_404(Tag, id=tag_id))

        for ingredient in validated_data.pop('ingredients'):
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            )
        return super().update(instance, validated_data)


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class FollowSerializer(serializers.ModelSerializer):
    queryset = User.objects.all()
    follower = serializers.PrimaryKeyRelatedField(queryset=queryset)
    followee = serializers.PrimaryKeyRelatedField(queryset=queryset)

    class Meta:
        model = Follow
        fields = ('follower', 'followee',)
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('follower', 'followee'),
                message='Нельзя подписаться повторно'
            )
        ]

    def validate(self, attrs):
        follower = attrs.get('follower')
        followee = attrs.get('followee')
        if follower == followee:
            raise serializers.ValidationError('Нельзя подписаться на себя')
        return attrs


class FolloweeSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='followee.email')
    id = serializers.ReadOnlyField(source='followee.id')
    username = serializers.ReadOnlyField(source='followee.username')
    first_name = serializers.ReadOnlyField(source='followee.first_name')
    last_name = serializers.ReadOnlyField(source='followee.last_name')
    is_subscribed = serializers.ReadOnlyField(source='followee.is_subscribed')
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count',
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        queryset = Recipe.objects.filter(author=obj.followee)
        recipes_limit = request.GET.get('recipes_limit')
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        return RecipeMinifiedSerializer(
            queryset, many=True, context={'request': request}
        ).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.followee).count()


class BookmarkSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = Bookmark
        fields = ('user', 'recipe',)


class ShoppingListSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe',)
