import pytest
from django.test import Client, RequestFactory
from django.urls import reverse
from MainApp.views import index_page


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