from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Tag(models.Model):
    """Модель Тег"""

    name = models.CharField(
        'Название',
        max_length=100,
    )

    color = models.CharField(
        'Цвет',
        max_length=50,
    )

    slug = models.SlugField(
        'Код',
        unique=True,
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель Ингредиент"""

    name = models.CharField(
        'Название',
        max_length=100,
    )

    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=10,
    )

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"


class Recipe(models.Model):
    """Модель Рецепт"""

    name = models.CharField(
        'Название',
        max_length=100
    )

    text = models.CharField(
        'Описание',
        max_length=500,
    )

    image = models.ImageField(
        'Фото',
        upload_to='recipes/images/',
        blank=True,
        null=True,
    )

    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes',
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        blank=False,
        related_name='recipes',
        through='RecipeIngredient',
    )

    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        blank=True,
        related_name='recipes',
    )

    pub_date = models.DateTimeField(auto_now_add=True)

    cooking_time = models.IntegerField(
        'Время приготовления',
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-pub_date',)


class RecipeIngredient(models.Model):
    """Связующая модель для Рецепт и Ингредиент"""

    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )

    amount = models.PositiveIntegerField(
        'Количество',
    )


class Follow(models.Model):
    """Модель Подписки"""

    follower = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='follower'
    )

    followee = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='followee'
    )

    def __str__(self):
        return f"{self.follower} подписан на {self.followee}"

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['follower', 'followee'],
            name='follow_unique'
        )]


class Bookmark(models.Model):
    """Модель Избранного"""

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='bookmarks',
    )

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='bookmarks',
    )

    def __str__(self):
        return f"{self.recipe} в закладках у {self.user}"

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='bookmark_unique'
        )]


class ShoppingList(models.Model):
    """Модель Списка покупок"""

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        blank=False,
        null=True,
        related_name='shopping_list',
    )

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        blank=False,
        null=True,
        related_name='shopping_list',
    )

    def __str__(self):
        return f"{self.recipe} в списке у {self.user}"

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='recipe_unique'
        )]
