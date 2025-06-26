from django.db import models

LANG_CHOICES = [
    ("python", "Python"),
    ("cpp", "C++"),
    ("java", "Java"),
    ("javascript", "JavaScript")
]

LANG_ICON = {
    "python": "fa-brands fa-python",
    "javascript": "fa-brands fa-js",
    "java": "fa-brands fa-java",
}

class Snippet(models.Model):
    name = models.CharField(max_length=100)  # -> input
    lang = models.CharField(max_length=30, choices=LANG_CHOICES)
    code = models.TextField(max_length=5000)  # -> textarea
    creation_date = models.DateTimeField(auto_now=True)
    views_count = models.PositiveIntegerField(default=0)
