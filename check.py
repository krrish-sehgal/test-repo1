
def process_data(data: list, limit: int = 100):
processed = [d for d in data if d < limit]
return processed


from django.db import models

class User(models.Model):
username = models.CharField(max_length=150)
email = models.EmailField(unique=True)

