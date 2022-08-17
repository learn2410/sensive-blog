from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Prefetch

from blog.models import Post, Tag, Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_per_page = 25
    list_display = ('id','title','published_at')
    # list_filter = ['author']
    raw_id_fields = ('author', 'tags', 'likes')

admin.site.register(Tag)


class Ptrfetch(object):
    pass


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_per_page = 25
    raw_id_fields = ('author', 'post')
    list_display = ('post','author','text','published_at')
    search_fields = ('text',)
    ordering=('pk',)
    # list_filter = ['post','author']

    def get_queryset(self, request):
        queryset = super(CommentAdmin, self).get_queryset(request)
        queryset = queryset.prefetch_related(
            Prefetch('author',queryset=User.objects.only('username')),
            Prefetch('post',queryset=Post.objects.only('title')))
        return queryset