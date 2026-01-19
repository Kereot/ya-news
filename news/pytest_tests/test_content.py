from django.conf import settings
from django.urls import reverse

import pytest

from news.forms import CommentForm


def test_news_count(client, news_list):
    response = client.get(reverse('news:home'))
    news_count = response.context['object_list'].count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, news_list):
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    all_dates = [item.date for item in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert sorted_dates == all_dates


def test_comments_order(client, test_news_detail_url, comment_list):
    response = client.get(test_news_detail_url)
    assert 'news' in response.context
    news_item = response.context['news']
    all_comments = news_item.comment_set.all()
    all_timestamps = [comment_item.created for comment_item in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert sorted_timestamps == all_timestamps


@pytest.mark.parametrize(
    'parametrized_client, form_available',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
def test_detail_page_form_availability(
        parametrized_client,
        form_available,
        test_news_detail_url
):
    response = parametrized_client.get(test_news_detail_url)
    assert ('form' in response.context) is form_available
    if form_available:
        assert isinstance(response.context['form'], CommentForm)
