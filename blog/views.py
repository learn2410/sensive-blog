from django.shortcuts import render

from blog.models import Comment, Post, Tag


def get_serialized_posts(ids):
    query = Post.objects.get_augmented_posts(ids)
    serialized_posts = {}
    for post in query:
        serialized_tags = [{'title': tag.title, 'posts_with_tag': tag.posts_count}
                           for tag in post.tags.all()]
        serialized_posts.update({
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
    return serialized_posts


def get_popular_tags_serialized(quantity):
    return [{'title': tag.title, 'posts_with_tag': tag.posts_count}
            for tag in Tag.objects.popular()[:quantity]]


def index(request):
    popular_ids = Post.objects.popular_ordered_ids(5)
    fresh_ids = Post.objects.fresh_ordered_ids(5)
    posts = get_serialized_posts(popular_ids + fresh_ids)

    context = {
        'most_popular_posts': [posts[post_id] for post_id in popular_ids],
        'page_posts': [posts[post_id] for post_id in fresh_ids],
        'popular_tags': get_popular_tags_serialized(5),
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = Post.objects.get(slug=slug)
    popular_posts_ids = Post.objects.popular_ordered_ids(5)
    posts = get_serialized_posts(popular_posts_ids+[post.id])

    comments = Comment.objects.filter(post=post.id).select_related('author')
    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': posts[post.id]['author'],
        'comments': serialized_comments,
        'likes_amount': post.likes.count(),
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': posts[post.id]['tags'],
    }

    context = {
        'post': serialized_post,
        'popular_tags': get_popular_tags_serialized(5),
        'most_popular_posts': [posts[post_id] for post_id in popular_posts_ids],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)

    popular_posts_ids = Post.objects.popular_ordered_ids(5)
    related_posts_ids = tag.posts.fresh_ordered_ids(20)
    posts = get_serialized_posts(popular_posts_ids + related_posts_ids)

    context = {
        'tag': tag.title,
        'popular_tags': get_popular_tags_serialized(5),
        'posts': [posts[post_id] for post_id in related_posts_ids],
        'most_popular_posts': [posts[post_id] for post_id in popular_posts_ids],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
