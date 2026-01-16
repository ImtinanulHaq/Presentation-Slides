# Generated migration for adding bullet_style field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('presentation_app', '0006_presentation_slide_ratio_presentation_template'),
    ]

    operations = [
        migrations.AddField(
            model_name='presentation',
            name='bullet_style',
            field=models.CharField(
                choices=[
                    ('numbered', 'Numbered (1, 2, 3...)'),
                    ('bullet_elegant', 'Elegant Bullets (●)'),
                    ('bullet_modern', 'Modern Bullets (▸)'),
                    ('bullet_professional', 'Professional Bullets (■)'),
                ],
                default='numbered',
                help_text='Style for bullet points: numbered, elegant, modern, or professional',
                max_length=50,
            ),
        ),
    ]
