from django.contrib.auth.models import User
from django.db import models, connection
from django.db.models import Count, F, Prefetch
from django.db.models.functions import Left
from django.urls import reverse


class PostQuerySet(models.QuerySet):

    def popular_ids(self, quantity):
        sql = f"""SELECT post_id, COUNT(*) as likes_count 
                FROM blog_post_likes
                GROUP BY post_id 
                ORDER BY likes_count DESC 
                LIMIT {quantity};"""
        with connection.cursor() as cursor:
            cursor.execute(sql)
            likes_count = list(dict(cursor.fetchall()))
        return likes_count

    def fresh_ids(self, quantity):
        return list(self.only('id').order_by('-published_at').values_list('id', flat=True)[:quantity])

    def serialized(self, ids):
        prefetched_comments = Prefetch(
            'comments',
            queryset=(Comment.objects.filter(post__in=ids).only('post'))
        )
        prefetched_tags = Prefetch(
            'tags',
            queryset=Tag.objects.all().annotate(posts_count=Count('posts'))
        )
        query = (self
                 .filter(id__in=ids)
                 .select_related('author')
                 .prefetch_related(prefetched_comments, prefetched_tags)
                 .annotate(teaser_text=Left('text', 200))
                 .annotate(author_name=F('author__username'))
                 .annotate(comments_amount=Count('comments'))
                 .defer('text', 'likes')
                 )
        result = {}
        for post in query:
            serialized_tags = [{'title': tag.title, 'posts_with_tag': tag.posts_count}
                               for tag in post.tags.all()]
            result.update({
                post.id: {
                    'title': post.title,
                    'teaser_text': post.teaser_text,
                    'author': post.author_name,
                    'image_url': post.image.url if post.image else None,
                    'published_at': post.published_at,
                    'slug': post.slug,
                    'comments_amount': post.comments_amount,
                    'tags': serialized_tags,
                    'first_tag_title': serialized_tags[0]['title'],
                }
            })
        return result


class Post(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    text = models.TextField('Текст')
    slug = models.SlugField('Название в виде url', max_length=200)
    image = models.ImageField('Картинка')
    published_at = models.DateTimeField('Дата и время публикации')

    objects = PostQuerySet.as_manager()

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        limit_choices_to={'is_staff': True})
    likes = models.ManyToManyField(
        User,
        related_name='liked_posts',
        verbose_name='Кто лайкнул',
        blank=True)
    tags = models.ManyToManyField(
        'Tag',
        related_name='posts',
        verbose_name='Теги')

    objects = PostQuerySet.as_manager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args={'slug': self.slug})

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'пост'
        verbose_name_plural = 'посты'


class TagQuerySet(models.QuerySet):
    def popular(self):
        return self.annotate(posts_count=Count('posts')).order_by('-posts_count')

    def most_popular_serialized(self, quantity):
        return [{'title': tag.title, 'posts_with_tag': tag.posts_count}
                for tag in self.popular()[:quantity]]



class Tag(models.Model):
    title = models.CharField('Тег', max_length=20, unique=True)

    objects = TagQuerySet.as_manager()

    def __str__(self):
        return self.title

    def clean(self):
        self.title = self.title.lower()

    def get_absolute_url(self):
        return reverse('tag_filter', args={'tag_title': self.slug})

    class Meta:
        ordering = ['title']
        verbose_name = 'тег'
        verbose_name_plural = 'теги'


class Comment(models.Model):
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост, к которому написан')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор')

    text = models.TextField('Текст комментария')
    published_at = models.DateTimeField('Дата и время публикации')

    def __str__(self):
        return f'{self.author.username} under {self.post.title}'

    class Meta:
        ordering = ['published_at']
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
