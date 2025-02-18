from django.contrib import admin
from .models import Post, Comment, Vote

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'slug', 'updated')
    list_filter = ('updated', )
    search_fields = ('slug', )
    prepopulated_fields = {'slug' : ('body', )}
    row_id_fields = ('user', )

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'body', 'is_replay', 'created')
    raw_id_fields = ('user', 'post', 'reply')

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    pass