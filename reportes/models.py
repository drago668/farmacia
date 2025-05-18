from django.db import models

class SearchTerm(models.Model):
    term = models.CharField(max_length=255, unique=True)
    total_searches = models.IntegerField(default=0)
    updated_on = models.DateTimeField(auto_now=True)
    category = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.term

class SearchQuery(models.Model):
    term = models.ForeignKey(SearchTerm, on_delete=models.CASCADE, related_name="queries")
    timestamp = models.DateTimeField(auto_now_add=True)
    sort_option = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.term.term} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"