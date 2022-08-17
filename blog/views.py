from django.shortcuts import render

from blog.models import Comment, Post, Tag


def index(request):
    popular_ids = Post.objects.popular_ids(5)
    fresh_ids = Post.objects.fresh_ids(5)
    posts = Post.objects.serialized(popular_ids + fresh_ids)

    context = {
        'most_popular_posts': [posts[post_id] for post_id in popular_ids],
        'page_posts': [posts[post_id] for post_id in fresh_ids],
        'popular_tags': Tag.objects.most_popular_serialized(5),
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = Post.objects.get(slug=slug)

    comments = Comment.objects.filter(post=post.id).select_related('author')
    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })

    related_tags = post.tags.popular().serialized()

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': post.likes.count(),
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': related_tags,
    }

    popular_posts_ids = Post.objects.popular_ids(5)
    posts = Post.objects.serialized(popular_posts_ids)
    context = {
        'post': serialized_post,
        'popular_tags': Tag.objects.most_popular_serialized(5),
        'most_popular_posts': [posts[post_id] for post_id in popular_posts_ids],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)

    popular_posts_ids = Post.objects.popular_ids(5)
    related_posts_ids = tag.posts.fresh_ids(20)
    posts = Post.objects.serialized(popular_posts_ids + related_posts_ids)

    context = {
        'tag': tag.title,
        'popular_tags': Tag.objects.most_popular_serialized(5),
        'posts': [posts[post_id] for post_id in related_posts_ids],
        'most_popular_posts': [posts[post_id] for post_id in popular_posts_ids],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
