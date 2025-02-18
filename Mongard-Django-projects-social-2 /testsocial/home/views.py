from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from home.models import Post, Comment, Vote
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import PostCreateUpdateForm, PostCommentForm, ReplyPostCommentForm, PostSearchForm
from django.utils.text import slugify
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


class HomeView(View):
    form_search_class = PostSearchForm

    def setup(self, request, *args, **kwargs):
        self.post_instance = Post.objects.all()
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        posts = self.post_instance
        search_form = self.form_search_class
        if request.GET.get('search'):
            posts = posts.filter(body__contains=request.GET['search'])
        return render(request, 'home/index.html', {'posts': posts, 'search_form': search_form})

    def post(self, request):
        return render(request, 'home/index.html')


class PostDetailView(View):
    form_class = PostCommentForm
    reply_form_class = ReplyPostCommentForm

    def setup(self, request, *args, **kwargs):
        self.post_instance = Post.objects.get(pk=kwargs['post_id'], slug=kwargs['post_slug'])
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        post = self.post_instance
        can_like = False
        if request.user.is_authenticated and self.post_instance.user_can_like(request.user):
            can_like = True
        comments = post.post_comments.filter(is_replay=False)
        comments_form = self.form_class()
        return render(request, 'home/detail.html', {'post': post, 'comments': comments, 'comments_form': comments_form, 'reply_form': self.reply_form_class, 'can_like': can_like})

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        post = self.post_instance
        comments_form = self.form_class(request.POST)
        if comments_form.is_valid():
            new_comment = comments_form.save(commit=False)
            new_comment.post = post
            new_comment.user = request.user
            new_comment.save()
            messages.success(request, 'comment sent successfully', 'success')
        return redirect('home:post_detail',post_id=post.id, post_slug=post.slug)



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


class ReplyPostCommentView(LoginRequiredMixin, View):
    reply_form = ReplyPostCommentForm

    def setup(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, id=kwargs['post_id'])
        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        post = self.post_instance
        comment = get_object_or_404(Comment, id=kwargs['comment_id'])
        form = self.reply_form(request.POST)
        if form.is_valid():
            new_reply = form.save(commit=False)
            new_reply.post = post
            new_reply.user = request.user
            new_reply.reply = comment
            new_reply.is_replay = True
            new_reply.save()
            messages.success(request, 'reply sent successfully', 'success')
        return redirect('home:post_detail', post.id, post.slug)


class PostLikeView(LoginRequiredMixin, View):

    def setup(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, id=kwargs['post_id'])
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        post = self.post_instance
        like = Vote.objects.filter(user=request.user, post=post)
        if like.exists():
            messages.error(request, 'You have already liked this post.', 'danger')
        else:
            Vote.objects.create(user=request.user, post=post)
            messages.success(request, 'You like this post.', 'success')
        return redirect('home:post_detail', post.id, post.slug)





