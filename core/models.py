from django.db import models


class SavedPlace(models.Model):
    user = models.ForeignKey('authsystem.User', on_delete=models.CASCADE, related_name='saved_places')
    name = models.CharField(max_length=100)
    address = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'saved_places'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.user.phone_number}"
