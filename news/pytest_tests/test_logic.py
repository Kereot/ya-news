from http import HTTPStatus

from django.urls import reverse

import pytest

from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_anonymous_user_cant_create_comment(
        client,
        comment_form_data,
        test_news_detail_url
):
    client.post(test_news_detail_url, data=comment_form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(
        not_author,
        not_author_client,
        news,
        comment_form_data,
        test_news_detail_url
):
    response = not_author_client.post(
        test_news_detail_url,
        data=comment_form_data
    )
    assertRedirects(response, f'{test_news_detail_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == comment_form_data['text']
    assert comment.news == news
    assert comment.author == not_author


def test_user_cant_use_bad_words(author_client, test_news_detail_url):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(test_news_detail_url, data=bad_words_data)
    form = response.context['form']
    assertFormError(
        form=form,
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.parametrize(
    'parametrized_client, expected_status, comments_quantity',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.FOUND, 0),
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND, 1),
    )
)
def test_delete_comment_accessibility(
        parametrized_client,
        expected_status,
        comments_quantity,
        author_client,
        comment_id,
        test_news_detail_url
):
    delete_url = reverse('news:delete', args=comment_id)
    response = parametrized_client.delete(delete_url)
    if parametrized_client == author_client:
        assertRedirects(
            response,
            test_news_detail_url + '#comments'
        )
    assert response.status_code == expected_status
    comments_count = Comment.objects.count()
    assert comments_count == comments_quantity


@pytest.mark.parametrize(
    'parametrized_client, expected_status, text_in_comment',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.FOUND,
         pytest.lazy_fixture('new_comment_text')),
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND,
         pytest.lazy_fixture('comment_text')),
    )
)
def test_edit_comment_accessibility(
        parametrized_client,
        expected_status,
        text_in_comment,
        new_comment_text,
        author_client,
        comment,
        comment_id,
        test_news_detail_url
):
    edit_url = reverse('news:edit', args=comment_id)
    response = parametrized_client.post(
        edit_url,
        data={'text': new_comment_text}
    )
    if parametrized_client == author_client:
        assertRedirects(
            response,
            test_news_detail_url + '#comments'
        )
    assert response.status_code == expected_status
    comment.refresh_from_db()
    assert comment.text == text_in_comment
