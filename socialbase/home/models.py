from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Post(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField()
    slug = models.SlugField(max_length=100)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated']

    def get_absolute_url(self):
        return reverse('home:post_detail', args= (self.id, self.slug))

    def likes_count(self):
        return self.post_likes.count()

    def user_can_like(self, user):
        user_like = user.user_likes.filter(post=self)
        if user_like.exists():
            return True
        return False

    def __str__(self):
        return f'{self.title} - {self.author}'


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comments')
    reply = models.ForeignKey('self', on_delete=models.CASCADE, related_name='reply_comments', null=True, blank=True)
    is_reply = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    body = models.TextField(max_length=400)

    def __str__(self):
        return f'{self.post.title} - {self.user}'


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_likes')

    def __str__(self):
        return f'{self.user.username} liked {self.post.title}'
