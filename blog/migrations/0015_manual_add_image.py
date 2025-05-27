from django.db import migrations, models
import cloudinary_storage.storage

class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0013_alter_post_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, null=True, storage=cloudinary_storage.storage.MediaCloudinaryStorage(), upload_to='post_images/'),
        ),
    ] 