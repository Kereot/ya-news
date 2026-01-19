from datetime import datetime, timedelta

from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

import pytest

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news(author):
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def news_id(news):
    return (news.id,)


@pytest.fixture
def test_news_detail_url(news_id):
    return reverse('news:detail', args=news_id)


@pytest.fixture
def comment_text():
    return 'comment_text'


@pytest.fixture
def comment(news, author, comment_text):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text=comment_text
    )
    return comment


@pytest.fixture
def comment_id(comment):
    return (comment.id,)


@pytest.fixture
def news_list(db):
    today = datetime.today()
    News.objects.bulk_create(
        (
            News(
                title=f'Новость {index}',
                text='Просто текст.',
                date=today - timedelta(days=index),
            )
            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        )
    )


@pytest.fixture
def comment_list(news, author):
    now = timezone.now()
    for i in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {i}'
        )
        comment.created = now + timedelta(days=i)
        comment.save()


@pytest.fixture
def comment_form_data(comment_text):
    return {'text': comment_text}


@pytest.fixture
def new_comment_text():
    return 'new_comment_text'
