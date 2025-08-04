import pytest
from MainApp.models import Snippet, Tag, Comment
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestSnippetModel:
    def test_create_snippet(self):
        """Тест для создания нового Сниппета"""
        snippet = Snippet.objects.create(
            name="Test Snippet",
            lang="python",
            code="snippet code"
        )

        assert snippet.name == "Test Snippet"
        assert snippet.lang == "python"
        assert snippet.public is True
        assert snippet.user is None

    def test_snippet_with_user(self):
        """Тест создания Сниппета с пользователем"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

        snippet = Snippet.objects.create(
            name="User Snippet",
            lang="javascript",
            code="console.log('Hello');",
            user=user,
            public=False
        )

        assert snippet.user == user
        assert snippet.public is False
        assert snippet.code == "console.log('Hello');"


@pytest.mark.django_db
class TestTagModel:
    """Тесты для модели Tag"""

    def test_tag_creation(self):
        """Тест создания тега"""
        tag = Tag.objects.create(name="Python")
        assert tag.name == "Python"

    def test_duplicate_tag_names_not_allowed(self):
        """Тест, что теги с одинаковыми именами недопустимы"""
        from django.db import IntegrityError, transaction

        # Создаем первый тег
        tag1 = Tag.objects.create(name="Python")

        # Пытаемся создать второй тег с тем же именем
        # Должно возникнуть исключение IntegrityError
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Tag.objects.create(name="Python")

        # Проверяем, что в базе данных остался только один тег с именем "Python"
        assert Tag.objects.filter(name="Python").count() == 1
        assert Tag.objects.get(name="Python") == tag1


@pytest.mark.django_db
class TestCommentModel:
    """Тесты для модели Comment"""

    def test_comment_creation(self):
        """Тест создания комментария"""
        # 1. Создать пользователя
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        # 2. Создать Сниппет
        snippet = Snippet.objects.create(
            name="User Snippet",
            lang="javascript",
            code="console.log('Hello');",
            user=user,
            public=False
        )
        # 3. Создать комментарий от имени пользователя, под Снипетом
        comment = Comment.objects.create(
            text="Тестовый комментарий",
            author=user,
            snippet=snippet
        )
        # 4. Проверим, что комментарий принадлежит отпред. польлзователю и добавлен под опред. сниппетом
        assert comment.author == user
        assert comment.snippet == snippet
        assert comment.text == "Тестовый комментарий"
