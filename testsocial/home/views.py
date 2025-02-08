from django.shortcuts import render, redirect
from django.views import View
from home.models import Post
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import PostCreateUpdateForm
from django.utils.text import slugify
from django.contrib import messages


class HomeView(View):

    def setup(self, request, *args, **kwargs):
        self.post_instance = Post.objects.all()
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        posts = self.post_instance
        return render(request, 'home/index.html', {'posts': posts})

    def post(self, request):
        return render(request, 'home/index.html')


class PostDetailView(View):

    def setup(self, request, *args, **kwargs):
        self.post_instance = Post.objects.get(pk=kwargs['post_id'], slug=kwargs['post_slug'])
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        post = self.post_instance
        return render(request, 'home/detail.html', {'post': post})


class PostCreateView(LoginRequiredMixin, View):
    form_class = PostCreateUpdateForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, 'home/create.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.slug = slugify(new_post.body[:30])
            new_post.user = request.user
            new_post.save()
            messages.success(request, 'New post created!', 'success')
            return redirect('home:post_detail', new_post.id, new_post.slug )


class PostUpdateView(LoginRequiredMixin, View):
    form_class = PostCreateUpdateForm

    def setup(self, request, *args, **kwargs):
        self.post_instance = Post.objects.get(pk=kwargs['post_id'])
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        post = self.post_instance
        if not post.user.id == request.user.id:
            messages.error(request, 'You are not authorized to edit this post.', 'danger')
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        post = self.post_instance
        form = self.form_class(instance=post)
        return render(request, 'home/update.html', {'form': form, 'post': post})

    def post(self, request, *args, **kwargs):
        post = self.post_instance
        form = self.form_class(request.POST, instance=post)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.slug = slugify(new_post.body[:30])
            new_post.user = request.user
            new_post.save()
            messages.success(request, 'New post updated!', 'success')
            return redirect('home:post_detail', new_post.id, new_post.slug )
        return render(request, 'home/update.html', {'form': form, 'post': post})


class PostDeleteView(LoginRequiredMixin, View):

    def setup(self, request, *args, **kwargs):
        self.post_instance = Post.objects.get(pk=kwargs['post_id'])
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        post = self.post_instance
        if not post.user.id == request.user.id:
            messages.error(request, 'You are not authorized to delete this post.', 'danger')
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        post = self.post_instance
        post.delete()
        messages.success(request, 'Post deleted!', 'success')
        return redirect('home:home')

