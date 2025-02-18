from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Like, Comment
from django.views import View
from .forms import CreatePostForm, UpdatePostForm, CommentForm, SearchForm, ReplyForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify

class HomePageView(View):

    def setup(self, request, *args, **kwargs):
        self.post_instance = Post.objects.all()
        return super().setup(request,*args, **kwargs)

    def get(self, request):
        posts = self.post_instance
        return render(request, 'home/index.html', {'posts': posts})


class PostDetailView(View):
    form_class_comment = CommentForm
    form_class_reply = ReplyForm

    def setup(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, id=kwargs['post_id'], slug=kwargs['post_slug'])
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        post = self.post_instance
        comments = post.post_comments.filter(is_reply=False)
        can_like = False
        if request.user.is_authenticated and post.user_can_like(request.user):
            can_like = True
        return render(request, 'home/post_details.html', {'post': post,'comment_form': self.form_class_comment, 'comments': comments, 'reply_form': self.form_class_reply, 'can_like': can_like})

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = self.form_class_comment(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.user = request.user
            new_comment.post = self.post_instance
            new_comment.save()
            messages.success(request, 'Comment successfully saved', 'success')
            return redirect('home:post_detail', self.post_instance.id, self.post_instance.slug)




class PostCreateView(LoginRequiredMixin, View):
    form_class = CreatePostForm

    def get(self, request):
        form = self.form_class()
        return render(request, 'home/create_post.html', {'form':form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            Post.objects.create(
                title= cd['title'],
                body = cd['body'],
                author = request.user,
                slug = slugify(cd['title'])
            )
            messages.success(request, 'Your post was created.', extra_tags='success')
        return redirect('home:home')


class PostUpdateView(LoginRequiredMixin, View):
    form_class = UpdatePostForm

    def setup(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, id=kwargs['post_id'])
        return super().setup(request, *args, **kwargs)
    
    def dispatch(self, request, *args, **kwargs):
        post = self.post_instance
        if post.author != request.user:
            messages.error(request, 'You are not able to edit this post...', extra_tags='danger')
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        post = self.post_instance
        form = self.form_class(instance=post)
        return render(request, 'home/post_update.html', {'form':form})

    def post(self, request, *args, **kwargs):
        post = self.post_instance
        form = self.form_class(request.POST, instance=post)
        if form.is_valid():
            cd = form.cleaned_data
            update_post = form.save(commit=False)
            update_post.author = request.user
            update_post.slug = slugify(cd['title'])
            update_post.save()
            messages.success(request, 'Your post was updated.', extra_tags='success')
        return redirect('home:post_detail', post.id, post.slug)


class PostDeleteView(LoginRequiredMixin, View):

    def setup(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, id=kwargs['post_id'])
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        post = self.post_instance
        if request.user.id == post.author.id:
            post.delete()
            messages.success(request, 'Your post was deleted.', extra_tags='success')
        else:
            messages.error(request, 'You are not allowed to delete this post.', extra_tags='danger')
        return redirect('home:home')


class PostLikeView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        post = get_object_or_404(Post, id=kwargs['post_id'])
        like = Like.objects.filter(post=post, user=request.user)
        if like.exists():
            messages.error(request, 'You are already liked.', extra_tags='danger')
        else:
            Like.objects.create(post=post, user=request.user)
            messages.success(request, 'You are now liked.', extra_tags='success')
        return redirect('home:post_detail', post.id, post.slug)


class PostAddReplyView(LoginRequiredMixin, View):
    form_class = ReplyForm

    def post(self, request, *args, **kwargs):
        post = get_object_or_404(Post, id=kwargs['post_id'] )
        comment = get_object_or_404(Comment, id=kwargs['comment_id'])
        form = self.form_class(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.post = post
            reply.reply = comment
            reply.is_reply = True
            reply.save()
            messages.success(request, 'reply added successfully...', 'success')
        return redirect('home:post_detail', post.id, post.slug)



    
    
