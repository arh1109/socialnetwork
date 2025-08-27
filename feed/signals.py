from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Media

@receiver(post_delete, sender=Media)
def delete_media_files(sender, instance: Media, **kwargs):
    # Delete original file
    try:
        if instance.file:
            instance.file.delete(save=False)
    except Exception:
        pass
    # Delete thumbnail (if your model has one and it may be set)
    try:
        if hasattr(instance, "thumbnail") and instance.thumbnail:
            instance.thumbnail.delete(save=False)
    except Exception:
        pass
