from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'slug', 'updated')
    list_filter = ('updated', )
    search_fields = ('slug', )
    prepopulated_fields = {'slug' : ('body', )}
    row_id_fields = ('user', )