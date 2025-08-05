import pytest
from django.test import Client, RequestFactory
from django.urls import reverse
from MainApp.views import index_page, add_snippet_page, snippet_edit, snippet_delete, snippet_detail
from MainApp.models import Snippet
from django.contrib.auth.models import User, AnonymousUser
from django.http import Http404
from MainApp.factories import UserFactory, SnippetFactory, TagFactory, CommentFactory


class TestIndexPage:
    def test_main_page_client(self):
        client = Client()
        response = client.get(reverse('home'))

        assert response.status_code == 200
        assert 'Добро пожаловать' in response.content.decode()
        assert response.context.get('pagename') == 'PythonBin'

    def test_main_page_factory(self):
        factory = RequestFactory()
        request = factory.get(reverse('home'))
        response = index_page(request)

        assert response.status_code == 200
        assert 'Добро пожаловать' in response.content.decode()


@pytest.mark.django_db
class TestAddSnippetPage:
    def setup_method(self):
        from django.test import RequestFactory
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_get_unauthenticated_redirect(self):
        request = self.factory.get(reverse('snippet-add'))
        request.user = AnonymousUser()
        response = add_snippet_page(request)
        # Проверяем, что неавторизованный пользователь получает редирект на логин
        assert response.status_code == 302
        assert '/login' in response.url

    def test_get_authenticated_ok(self):
        request = self.factory.get(reverse('snippet-add'))
        request.user = self.user
        response = add_snippet_page(request)
        assert response.status_code == 200
        assert 'Создание сниппета' in response.content.decode()

    def test_post_create_snippet(self):
        data = {
            'name': 'Test Snippet',
            'lang': 'python',
            'code': 'print("Hello")',
            'public': True,
        }
        request = self.factory.post(reverse('snippet-add'), data)
        request.user = self.user
        response = add_snippet_page(request)
        # После успешного создания должен быть редирект
        assert response.status_code == 302
        # Проверяем, что сниппет создан
        snippet = Snippet.objects.get(name='Test Snippet')
        assert snippet.code == 'print("Hello")'
        assert snippet.user == self.user


@pytest.mark.django_db
class TestSnippetDeletePage:
    def setup_method(self):
        self.factory = RequestFactory()

    def test_delete_snippet_incorrect_id(self):
        # 1. Создадим сниппет (id=1)
        Snippet.objects.create(
            name="User Snippet",
            lang="javascript",
            code="console.log('Hello');",
            public=True
        )
        # 2. Отправим запрос по несущ.id (id=9)
        request = self.factory.get(reverse('snippet-delete', kwargs={'id': 9}))
        with pytest.raises(Http404):
            response = snippet_delete(request, id=9)
        # assert response.status_code == 404
        # 3. Проверим, что исходный Сниппет на месте
        assert Snippet.objects.count() == 1

    def test_snippet_delete(self):
        Snippet.objects.create(
            name="User Snippet",
            lang="javascript",
            code="console.log('Hello');",
            public=True
        )
        request = self.factory.get(reverse('snippet-delete', kwargs={'id': 1}))
        response = snippet_delete(request, id=1)
        assert response.status_code == 302
        assert Snippet.objects.count() == 0


@pytest.mark.django_db
class TestSnippetsPage:
    def setup_method(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.another_user = User.objects.create_user(
            username="anotheruser",
            email="another@example.com",
            password="testpass123"
        )
        self.third_user = User.objects.create_user(
            username="thirduser",
            email="third@example.com",
            password="testpass123"
        )

        # Создаем множество тестовых сниппетов для более надежных тестов
        self.snippets = []

        # Сниппеты первого пользователя
        self.snippets.extend([
            Snippet.objects.create(
                name="Python Hello World",
                code="print('Hello, World!')",
                lang="python",
                user=self.user,
                public=True
            ),
            Snippet.objects.create(
                name="Python Calculator",
                code="def add(a, b):\n    return a + b",
                lang="python",
                user=self.user,
                public=True
            ),
            Snippet.objects.create(
                name="Private Python Snippet",
                code="print('This is private')",
                lang="python",
                user=self.user,
                public=False
            ),
            Snippet.objects.create(
                name="JavaScript Alert",
                code="alert('Hello from JS');",
                lang="javascript",
                user=self.user,
                public=True
            ),
            Snippet.objects.create(
                name="HTML Template",
                code="<html><body><h1>Hello</h1></body></html>",
                lang="html",
                user=self.user,
                public=True
            )
        ])

        # Сниппеты второго пользователя
        self.snippets.extend([
            Snippet.objects.create(
                name="Another Python Code",
                code="import os\nprint(os.getcwd())",
                lang="python",
                user=self.another_user,
                public=True
            ),
            Snippet.objects.create(
                name="CSS Styles",
                code="body { color: red; }",
                lang="css",
                user=self.another_user,
                public=True
            ),
            Snippet.objects.create(
                name="Private Another User Snippet",
                code="console.log('private');",
                lang="javascript",
                user=self.another_user,
                public=False
            )
        ])

        # Сниппеты третьего пользователя
        self.snippets.extend([
            Snippet.objects.create(
                name="SQL Query",
                code="SELECT * FROM users WHERE active = 1;",
                lang="sql",
                user=self.third_user,
                public=True
            ),
            Snippet.objects.create(
                name="Bash Script",
                code="#!/bin/bash\necho 'Hello from bash'",
                lang="bash",
                user=self.third_user,
                public=True
            )
        ])

    def test_my_snippets_authenticated_user(self):
        """Тест для просмотра своих сниппетов авторизованным пользователем"""
        self.client.force_login(self.user)
        response = self.client.get('/snippets/my')

        assert response.status_code == 200
        assert response.context['pagename'] == 'Мои сниппеты'
        # Проверяем, что видны только сниппеты текущего пользователя
        user_snippets = [s for s in self.snippets if s.user == self.user]
        assert len(response.context['page_obj']) == len(user_snippets)

    def test_my_snippets_anonymous_user(self):
        """Тест для просмотра своих сниппетов неавторизованным пользователем"""
        response = self.client.get('/snippets/my')

        assert response.status_code == 401  # возвращает 401

    def test_all_snippets_authenticated_user(self):
        """Тест для просмотра всех сниппетов авторизованным пользователем"""
        self.client.force_login(self.user)
        response = self.client.get('/snippets/list')

        assert response.status_code == 200
        assert response.context['pagename'] == 'Просмотр сниппетов'
        # Проверяем, что видны публичные сниппеты всех пользователей + приватные текущего
        public_snippets = [s for s in self.snippets if s.public]
        private_own_snippets = [s for s in self.snippets if not s.public and s.user == self.user]
        expected_count = len(public_snippets) + len(private_own_snippets)
        if expected_count > 5:
            expected_count = 5
        assert len(response.context['page_obj']) == expected_count

    def test_all_snippets_anonymous_user(self):
        """Тест для просмотра всех сниппетов неавторизованным пользователем"""
        response = self.client.get('/snippets/list')

        assert response.status_code == 200
        assert response.context['pagename'] == 'Просмотр сниппетов'
        # Проверяем, что видны только публичные сниппеты
        public_snippets = [s for s in self.snippets if s.public]
        assert len(response.context['page_obj']) == len(public_snippets)

    @pytest.mark.skip
    def test_snippets_with_search(self):
        """Тест поиска сниппетов"""
        self.client.force_login(self.user)
        response = self.client.get('/snippets/list?search=Python')

        assert response.status_code == 200
        # Проверяем, что найдены сниппеты с "Python" в названии или коде
        found_snippets = response.context['page_obj']
        assert len(found_snippets) > 0
        for snippet in found_snippets:
            assert 'Python' in snippet.name or 'Python' in snippet.code

    def test_snippets_with_lang_filter(self):
        """Тест фильтрации по языку"""
        self.client.force_login(self.user)
        response = self.client.get('/snippets/list?lang=python')

        assert response.status_code == 200
        assert response.context['lang'] == 'python'
        # Проверяем, что все найденные сниппеты имеют язык python
        found_snippets = response.context['page_obj']
        assert len(found_snippets) > 0
        for snippet in found_snippets:
            assert snippet.lang == 'python'

    def test_snippets_with_user_filter(self):
        """Тест фильтрации по пользователю"""
        self.client.force_login(self.user)
        response = self.client.get(f'/snippets/list?user_id={self.another_user.id}')

        assert response.status_code == 200
        assert response.context['user_id'] == str(self.another_user.id)
        # Проверяем, что найдены только сниппеты указанного пользователя
        found_snippets = response.context['page_obj']
        assert len(found_snippets) > 0
        for snippet in found_snippets:
            assert snippet.user == self.another_user

    def test_snippets_with_sorting(self):
        """Тест сортировки сниппетов"""
        self.client.force_login(self.user)
        response = self.client.get('/snippets/list?sort=name')

        assert response.status_code == 200
        assert response.context['sort'] == 'name'
        snippets_list = list(response.context['page_obj'])
        # Проверяем, что сниппеты отсортированы по имени
        for i in range(len(snippets_list) - 1):
            assert snippets_list[i].name <= snippets_list[i + 1].name

    def test_snippets_with_reverse_sorting(self):
        """Тест обратной сортировки сниппетов"""
        self.client.force_login(self.user)
        response = self.client.get('/snippets/list?sort=-name')

        assert response.status_code == 200
        assert response.context['sort'] == '-name'
        snippets_list = list(response.context['page_obj'])
        # Проверяем, что сниппеты отсортированы по имени в обратном порядке
        for i in range(len(snippets_list) - 1):
            assert snippets_list[i].name >= snippets_list[i + 1].name

    def test_snippets_with_lang_sorting(self):
        """Тест сортировки по языку"""
        self.client.force_login(self.user)
        response = self.client.get('/snippets/list?sort=lang')

        assert response.status_code == 200
        assert response.context['sort'] == 'lang'
        snippets_list = list(response.context['page_obj'])
        # Проверяем, что сниппеты отсортированы по языку
        for i in range(len(snippets_list) - 1):
            assert snippets_list[i].lang <= snippets_list[i + 1].lang

    def test_multiple_filters_combined(self):
        """Тест комбинирования нескольких фильтров"""
        self.client.force_login(self.user)
        response = self.client.get(f'/snippets/list?lang=python&user_id={self.user.id}&search=Hello')

        assert response.status_code == 200
        assert response.context['lang'] == 'python'
        assert response.context['user_id'] == str(self.user.id)
        # Проверяем, что найдены сниппеты, соответствующие всем фильтрам
        found_snippets = response.context['page_obj']
        for snippet in found_snippets:
            assert snippet.lang == 'python'
            assert snippet.user == self.user
            assert 'Hello' in snippet.name or 'Hello' in snippet.code

    def test_public_and_private_snippets_for_authenticated_user(self):
        """Тест доступа к публичным и приватным сниппетам для авторизованного пользователя"""
        self.client.force_login(self.user)
        response = self.client.get('/snippets/list')

        assert response.status_code == 200
        snippets_list = list(response.context['page_obj'])

        # Проверяем, что видны публичные сниппеты всех пользователей
        public_snippets = [s for s in self.snippets if s.public]
        for snippet in public_snippets:
            assert snippet in snippets_list

        # Проверяем, что видны приватные сниппеты текущего пользователя
        private_own_snippets = [s for s in self.snippets if not s.public and s.user == self.user]
        for snippet in private_own_snippets:
            assert snippet in snippets_list

        # Проверяем, что НЕ видны приватные сниппеты других пользователей
        private_others_snippets = [s for s in self.snippets if not s.public and s.user != self.user]
        for snippet in private_others_snippets:
            assert snippet not in snippets_list

    def test_only_public_snippets_for_anonymous_user(self):
        """Тест доступа только к публичным сниппетам для неавторизованного пользователя"""
        response = self.client.get('/snippets/list')

        assert response.status_code == 200
        snippets_list = list(response.context['page_obj'])

        # Проверяем, что видны только публичные сниппеты
        public_snippets = [s for s in self.snippets if s.public]
        for snippet in public_snippets:
            assert snippet in snippets_list

        # Проверяем, что НЕ видны приватные сниппеты
        private_snippets = [s for s in self.snippets if not s.public]
        for snippet in private_snippets:
            assert snippet not in snippets_list

    def test_pagination(self):
        """Тест пагинации"""
        self.client.force_login(self.user)
        response = self.client.get('/snippets/list')

        assert response.status_code == 200
        assert 'page_obj' in response.context
        # Проверяем, что пагинация работает (по 5 элементов на страницу)
        assert hasattr(response.context['page_obj'], 'has_other_pages')
        assert hasattr(response.context['page_obj'], 'number')
        assert hasattr(response.context['page_obj'], 'paginator')

    def test_empty_search_results(self):
        """Тест поиска с пустыми результатами"""
        self.client.force_login(self.user)
        response = self.client.get('/snippets/list?search=NonExistentSnippet')

        assert response.status_code == 200
        assert len(response.context['page_obj']) == 0

    def test_empty_lang_filter(self):
        """Тест фильтрации по несуществующему языку"""
        self.client.force_login(self.user)
        response = self.client.get('/snippets/list?lang=nonexistent')

        assert response.status_code == 200
        assert len(response.context['page_obj']) == 0


@pytest.mark.django_db
class TestSnippetDetail:
    def setup_method(self):
        self.factory = RequestFactory()
        self.client = Client()

        # Создаем тестовых пользователей с помощью фабрик
        self.user = UserFactory(username="testuser", email="test@example.com")
        self.another_user = UserFactory(username="anotheruser", email="another@example.com")

        # Создаем тестовые сниппеты с помощью фабрик
        self.public_snippet = SnippetFactory(
            name="Public Python Snippet",
            code="print('Hello, World!')",
            lang="python",
            user=self.user,
            public=True,
            views_count=5
        )

        self.private_snippet = SnippetFactory(
            name="Private Python Snippet",
            code="print('This is private')",
            lang="python",
            user=self.user,
            public=False,
            views_count=2
        )

        # Создаем комментарии к сниппетам с помощью фабрик
        self.comment1 = CommentFactory(
            text="Отличный код!",
            author=self.user,
            snippet=self.public_snippet
        )

        self.comment2 = CommentFactory(
            text="Очень полезно",
            author=self.another_user,
            snippet=self.public_snippet
        )

    def test_snippet_detail_public_snippet_authenticated_user(self):
        """Тест просмотра публичного сниппета авторизованным пользователем"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('snippet-detail', kwargs={'id': self.public_snippet.id}))

        assert response.status_code == 200
        assert response.context['pagename'] == f'Сниппет: {self.public_snippet.name}'
        assert response.context['snippet'] == self.public_snippet
        assert len(response.context['comments']) == 2

    def test_snippet_detail_public_snippet_anonymous_user(self):
        """Тест просмотра публичного сниппета неавторизованным пользователем"""
        response = self.client.get(reverse('snippet-detail', kwargs={'id': self.public_snippet.id}))

        assert response.status_code == 200
        assert response.context['snippet'] == self.public_snippet
        # assert 'comment_form' in response.context
        assert len(response.context['comments']) == 2

    def test_snippet_detail_private_snippet_owner(self):
        """Тест просмотра приватного сниппета его владельцем"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('snippet-detail', kwargs={'id': self.private_snippet.id}))

        assert response.status_code == 200
        assert response.context['snippet'] == self.private_snippet
        # assert 'comment_form' in response.context

    def test_snippet_detail_private_snippet_other_user(self):
        """Тест просмотра приватного сниппета другим пользователем"""
        self.client.force_login(self.another_user)
        response = self.client.get(reverse('snippet-detail', kwargs={'id': self.private_snippet.id}))

        assert response.status_code == 403

    def test_snippet_detail_private_snippet_anonymous_user(self):
        """Тест просмотра приватного сниппета неавторизованным пользователем"""
        response = self.client.get(reverse('snippet-detail', kwargs={'id': self.private_snippet.id}))

        assert response.status_code == 200
        assert response.context['snippet'] == self.private_snippet
        assert 'comment_form' in response.context

    def test_snippet_detail_nonexistent_snippet(self):
        """Тест просмотра несуществующего сниппета"""
        self.client.force_login(self.user)
        try:
            response = self.client.get(reverse('snippet-detail', kwargs={'id': 99999}))
            assert response.status_code == 404
        except Exception as e:
            # Django может вернуть 500 ошибку при DoesNotExist исключении
            assert "DoesNotExist" in str(e) or "Snippet matching query does not exist" in str(e)

    def test_snippet_detail_increments_views_count(self):
        """Тест увеличения счетчика просмотров при просмотре сниппета"""
        initial_views = self.public_snippet.views_count
        self.client.force_login(self.user)

        response = self.client.get(reverse('snippet-detail', kwargs={'id': self.public_snippet.id}))

        assert response.status_code == 200
        # Обновляем объект из базы данных
        self.public_snippet.refresh_from_db()
        assert self.public_snippet.views_count == initial_views + 1

    def test_snippet_detail_with_comments(self):
        """Тест отображения комментариев к сниппету"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('snippet-detail', kwargs={'id': self.public_snippet.id}))

        assert response.status_code == 200
        comments = response.context['comments']
        assert len(comments) == 2
        assert self.comment1 in comments
        assert self.comment2 in comments

    def test_snippet_detail_without_comments(self):
        """Тест отображения сниппета без комментариев"""
        # Создаем новый сниппет без комментариев с помощью фабрики
        snippet_without_comments = SnippetFactory(
            name="Snippet Without Comments",
            code="print('No comments')",
            lang="python",
            user=self.user,
            public=True
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse('snippet-detail', kwargs={'id': snippet_without_comments.id}))

        assert response.status_code == 200
        assert len(response.context['comments']) == 0

    def test_snippet_detail_comment_form_in_context(self):
        """Тест наличия формы комментария в контексте"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('snippet-detail', kwargs={'id': self.public_snippet.id}))

        assert response.status_code == 200
        assert 'comment_form' in response.context
        assert response.context['comment_form'] is not None

    def test_snippet_detail_using_request_factory(self):
        """Тест с использованием RequestFactory"""
        request = self.factory.get(reverse('snippet-detail', kwargs={'id': self.public_snippet.id}))
        request.user = self.user

        response = snippet_detail(request, self.public_snippet.id)

        assert response.status_code == 200
        # При использовании RequestFactory напрямую, response может не иметь context
        # Проверяем, что функция возвращает HttpResponse
        assert hasattr(response, 'content')

    def test_snippet_detail_multiple_views_increment_count(self):
        """Тест многократного увеличения счетчика просмотров"""
        initial_views = self.public_snippet.views_count
        self.client.force_login(self.user)

        # Просматриваем сниппет несколько раз
        for i in range(3):
            response = self.client.get(reverse('snippet-detail', kwargs={'id': self.public_snippet.id}))
            assert response.status_code == 200

        # Проверяем, что счетчик увеличился на 3
        self.public_snippet.refresh_from_db()
        assert self.public_snippet.views_count == initial_views + 3

    def test_snippet_detail_different_users_increment_count(self):
        """Тест увеличения счетчика просмотров разными пользователями"""
        initial_views = self.public_snippet.views_count

        # Первый пользователь просматривает
        self.client.force_login(self.user)
        response1 = self.client.get(reverse('snippet-detail', kwargs={'id': self.public_snippet.id}))
        assert response1.status_code == 200

        # Второй пользователь просматривает
        self.client.force_login(self.another_user)
        response2 = self.client.get(reverse('snippet-detail', kwargs={'id': self.public_snippet.id}))
        assert response2.status_code == 200

        # Проверяем, что счетчик увеличился на 2
        self.public_snippet.refresh_from_db()
        assert self.public_snippet.views_count == initial_views + 2

    def test_snippet_detail_context_structure(self):
        """Тест структуры контекста ответа"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('snippet-detail', kwargs={'id': self.public_snippet.id}))

        assert response.status_code == 200
        context = response.context

        # Проверяем наличие всех необходимых ключей в контексте
        assert 'pagename' in context
        assert 'snippet' in context
        assert 'comments' in context
        assert 'comment_form' in context

        # Проверяем правильность значений
        assert context['pagename'] == f'Сниппет: {self.public_snippet.name}'
        assert context['snippet'] == self.public_snippet
        # comments может быть QuerySet или list, проверяем что это итерируемый объект
        assert hasattr(context['comments'], '__iter__')
        assert context['comment_form'] is not None

    def test_snippet_detail_with_factory_generated_data(self):
        """Тест с данными, сгенерированными фабриками"""
        # Создаем сниппет с автоматически сгенерированными данными
        factory_snippet = SnippetFactory(
            user=self.user,
            public=True
        )

        # Создаем несколько комментариев к этому сниппету
        comments = CommentFactory.create_batch(3, snippet=factory_snippet)

        self.client.force_login(self.user)
        response = self.client.get(reverse('snippet-detail', kwargs={'id': factory_snippet.id}))

        assert response.status_code == 200
        assert response.context['snippet'] == factory_snippet
        assert len(response.context['comments']) == 3

    def test_snippet_detail_anonymous_snippet(self):
        """Тест просмотра сниппета без автора (анонимного)"""
        # Создаем сниппет без пользователя
        anonymous_snippet = SnippetFactory(user=None, public=True)

        response = self.client.get(reverse('snippet-detail', kwargs={'id': anonymous_snippet.id}))

        assert response.status_code == 200
        assert response.context['snippet'] == anonymous_snippet
        assert response.context['snippet'].user is None

    def test_snippet_detail_with_tags(self):
        """Тест просмотра сниппета с тегами"""
        # Создаем теги через фабрику
        from .factories import TagFactory
        python_tag = TagFactory(name='python')
        django_tag = TagFactory(name='django')
        web_tag = TagFactory(name='web')

        # Создаем сниппет с тегами
        snippet_with_tags = SnippetFactory(
            user=self.user,
            public=True
        )
        # Очищаем автоматически созданные теги и добавляем наши
        snippet_with_tags.tags.clear()
        snippet_with_tags.tags.add(python_tag, django_tag, web_tag)

        self.client.force_login(self.user)
        response = self.client.get(reverse('snippet-detail', kwargs={'id': snippet_with_tags.id}))

        assert response.status_code == 200
        assert response.context['snippet'] == snippet_with_tags
        assert snippet_with_tags.tags.count() == 3

    def test_snippet_detail_multiple_languages(self):
        """Тест просмотра сниппетов на разных языках"""
        # Создаем сниппеты на разных языках
        python_snippet = SnippetFactory(lang='python', user=self.user, public=True)
        js_snippet = SnippetFactory(lang='javascript', user=self.user, public=True)
        java_snippet = SnippetFactory(lang='java', user=self.user, public=True)

        self.client.force_login(self.user)

        # Проверяем каждый сниппет
        for snippet in [python_snippet, js_snippet, java_snippet]:
            response = self.client.get(reverse('snippet-detail', kwargs={'id': snippet.id}))
            assert response.status_code == 200
            assert response.context['snippet'] == snippet
            assert response.context['snippet'].lang in ['python', 'javascript', 'java']



#  Преимущества автотестов:
# 1. Экономия времени на проверку функционала
# 2. Обеспечение качества продукта в соответствии с требованиями
# 3. При доработке нового функционала, старый остается рабочим
# 4. С тестами удобно делать рефакторинг
# 5. Создание тестов, позволяет понять логику работы приложения