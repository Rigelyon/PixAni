import os
from django.conf import settings
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Deletes all files in the embedded_images directory'

    def handle(self, *args, **kwargs):
        embedded_images_path = os.path.join(settings.MEDIA_ROOT, 'embedded_images')
        if os.path.exists(embedded_images_path):
            for file_name in os.listdir(embedded_images_path):
                file_path = os.path.join(embedded_images_path, file_name)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        self.stdout.write(self.style.SUCCESS(f'Deleted: {file_path}'))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f'Error deleting {file_path}: {e}'))
        else:
            self.stdout.write(self.style.WARNING(f'Directory does not exist: {embedded_images_path}'))
