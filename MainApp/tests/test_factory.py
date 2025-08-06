import pytest
from MainApp.factories import UserFactory, SnippetFactory, TagFactory
from MainApp.models import User, Tag, Snippet


@pytest.mark.django_db
def test_task1():
    UserFactory(username="Alice")
    user = User.objects.get(id=1)


    assert user.username == 'Alice'
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_task2():
    TagFactory.create_batch(5)

    assert Tag.objects.count() == 5


@pytest.mark.django_db
def test_task6():
    user = UserFactory()
    SnippetFactory.create_batch(3, user=user, public=False)

    snippets = Snippet.objects.all()

    for snippet in snippets:
        assert snippet.user == user
        assert snippet.public is False

    assert len(snippets) == 3