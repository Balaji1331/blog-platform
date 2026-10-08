from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import PostForm, RegistrationForm
from .models import Post


def home(request):
    """All published posts. Search and category filtering happen live in the browser."""
    context = {
        "posts": Post.findAll(),
        "categories": ["All"] + [value for value, _ in Post.CATEGORY_CHOICES],
    }
    return render(request, "blog/home.html", context)


def post_detail(request, pk):
    post = get_object_or_404(Post.objects.select_related("author"), pk=pk)
    is_author = request.user.is_authenticated and post.author_id == request.user.id
    if not post.published and not is_author:
        raise Http404("Post not found")
    return render(request, "blog/post_detail.html", {"post": post, "is_author": is_author})


@login_required
def my_posts(request):
    return render(request, "blog/my_posts.html", {"posts": Post.findByAuthor(request.user.id)})


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        messages.success(request, "Post created successfully!")
        return redirect("my_posts")
    return render(request, "blog/post_form.html", {"form": form, "mode": "create"})


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author_id != request.user.id:
        messages.error(request, "You are not authorized to edit this post.")
        return redirect("post_detail", pk=post.pk)

    form = PostForm(request.POST or None, instance=post)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Post updated successfully!")
        return redirect("my_posts")
    return render(request, "blog/post_form.html", {"form": form, "mode": "edit", "post": post})


@login_required
@require_POST
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author_id != request.user.id:
        messages.error(request, "You are not authorized to delete this post.")
        return redirect("post_detail", pk=post.pk)
    post.delete()
    messages.success(request, "Post deleted successfully")
    return redirect("my_posts")


def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        auth_login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(request, "Welcome to BlogPlatform!")
        return redirect("home")
    return render(request, "blog/register.html", {"form": form})
