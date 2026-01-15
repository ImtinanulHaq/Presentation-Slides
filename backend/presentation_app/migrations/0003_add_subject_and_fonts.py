# Generated migration for adding subject and font fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('presentation_app', '0002_alter_slide_options_presentation_json_structure_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='presentation',
            name='subject',
            field=models.CharField(
                choices=[
                    ('general', 'General'),
                    ('english', 'English'),
                    ('urdu', 'Urdu'),
                    ('science', 'Science'),
                    ('biology', 'Biology'),
                    ('physics', 'Physics'),
                    ('medical', 'Medical Field'),
                    ('it', 'IT Field'),
                    ('engineering', 'Engineering Field'),
                ],
                default='general',
                max_length=50
            ),
        ),
        migrations.AddField(
            model_name='presentation',
            name='title_font',
            field=models.CharField(
                choices=[
                    ('arial', 'Arial'),
                    ('calibri', 'Calibri'),
                    ('georgia', 'Georgia'),
                    ('times', 'Times New Roman'),
                    ('verdana', 'Verdana'),
                ],
                default='calibri',
                max_length=50
            ),
        ),
        migrations.AddField(
            model_name='presentation',
            name='heading_font',
            field=models.CharField(
                choices=[
                    ('arial', 'Arial'),
                    ('calibri', 'Calibri'),
                    ('georgia', 'Georgia'),
                    ('times', 'Times New Roman'),
                    ('verdana', 'Verdana'),
                ],
                default='calibri',
                max_length=50
            ),
        ),
        migrations.AddField(
            model_name='presentation',
            name='content_font',
            field=models.CharField(
                choices=[
                    ('arial', 'Arial'),
                    ('calibri', 'Calibri'),
                    ('georgia', 'Georgia'),
                    ('times', 'Times New Roman'),
                    ('verdana', 'Verdana'),
                ],
                default='arial',
                max_length=50
            ),
        ),
        migrations.AddField(
            model_name='slide',
            name='fonts',
            field=models.JSONField(
                default=dict,
                blank=True
            ),
        ),
    ]
