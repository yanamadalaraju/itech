from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=[('Admin', 'Admin'), ('User', 'User')])

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Software(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    file = models.FileField(upload_to="software_files/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Check if the software is being updated and the file field is being changed
        if self.pk:
            existing_software = Software.objects.get(pk=self.pk)
            if existing_software.file != self.file:
                # Delete the existing file from storage if it is being replaced
                if existing_software.file:
                    existing_software.file.delete(save=False)
        
        super(Software, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
