import pytest
from MainApp.factories import TagFactory

@pytest.fixture
def tag_factory():
    def _create_tags(names: list[str]):
        tags = []
        for name in names:
            tags.append(TagFactory(name=name))
        return tags

    return _create_tags