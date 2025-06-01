from django.db import models
from django.contrib.auth.models import User

class Recipe(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    steps = models.TextField(verbose_name='Шаги приготовления')
    cooking_time = models.PositiveIntegerField(verbose_name='Время приготовления (мин.)')
    image = models.ImageField(upload_to='recipes/', null=True, blank=True, verbose_name='Изображение')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')

    def __str__(self):
        return self.title

class Comment(models.Model):
    """Комментарии к рецептам"""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(verbose_name='Текст комментария')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.recipe.title}"
