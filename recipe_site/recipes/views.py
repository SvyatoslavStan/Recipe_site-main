from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Q

from .models import Recipe
from .forms import RecipeForm, CustomUserCreationForm, CommentForm


def index(request):
    recipes = Recipe.objects.order_by('?')[:5]
    return render(request, 'recipes/index.html', {'recipes': recipes})


def recipe_list(request):
    """Отображает все рецепты + поиск по названию/описанию."""
    query = request.GET.get('q', '')
    recipes = Recipe.objects.all()
    if query:
        recipes = recipes.filter(Q(title__icontains=query) | Q(description__icontains=query))

    return render(request, 'recipes/recipe_list.html', {
        'recipes': recipes,
        'query': query,
    })


def recipe_detail(request, pk):
    """Детальный просмотр рецепта + вывод/добавление комментариев."""
    recipe = get_object_or_404(Recipe, pk=pk)
    comments = recipe.comments.order_by('-created_at')

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Вы должны быть авторизованы, чтобы оставлять комментарии.")
            return redirect('recipe_detail', pk=recipe.pk)

        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.recipe = recipe
            new_comment.author = request.user
            new_comment.save()
            return redirect('recipe_detail', pk=recipe.pk)
    else:
        form = CommentForm()

    return render(request, 'recipes/recipe_detail.html', {
        'recipe': recipe,
        'comments': comments,
        'form': form
    })


@login_required
def add_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            new_recipe = form.save(commit=False)
            new_recipe.author = request.user
            new_recipe.save()
            form.save_m2m()
            return redirect('recipe_detail', pk=new_recipe.pk)
    else:
        form = RecipeForm()
    return render(request, 'recipes/recipe_form.html', {'form': form, 'title': 'Добавить рецепт'})


@login_required
def edit_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if recipe.author != request.user:
        messages.error(request, "У вас нет прав редактировать этот рецепт!")
        return redirect('recipe_detail', pk=recipe.pk)

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            form.save()
            return redirect('recipe_detail', pk=recipe.pk)
    else:
        form = RecipeForm(instance=recipe)
    return render(request, 'recipes/recipe_form.html', {'form': form, 'title': 'Редактировать рецепт'})


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'recipes/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'recipes/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('index')
