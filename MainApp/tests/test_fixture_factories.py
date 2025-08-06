import pytest
from MainApp.factories import TagFactory, SnippetFactory, CommentFactory
from MainApp.models import Tag, Snippet, Comment


#

@pytest.mark.django_db
def test_factory_tags(tag_factory):
    tags = tag_factory(names=["js", "basic", "oop"])

    assert Tag.objects.count() == 3

    assert tags[0].name == "js"
    assert tags[1].name == "basic"
    assert tags[2].name == "oop"


@pytest.fixture
def comment_factory():
    def _create_comments(snippet, num=5):
        return CommentFactory.create_batch(num, snippet=snippet)
    return _create_comments


@pytest.mark.django_db
def test_factory_comments(comment_factory):
    # Добавит 6 произвольных комментариев к snippet
    snippet = SnippetFactory()
    comment_factory(snippet=snippet, num=6)

    comments = Comment.objects.all()
    assert Comment.objects.count() == 6

    for comment in comments:
        assert comment.snippet == snippet
