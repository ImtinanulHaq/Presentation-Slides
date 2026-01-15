# Generated migration for adding Noto Nastaliq Urdu font

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('presentation_app', '0003_add_subject_and_fonts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='presentation',
            name='title_font',
            field=models.CharField(
                choices=[
                    ('georgia', 'Georgia'),
                    ('times', 'Times New Roman'),
                    ('garamond', 'Garamond'),
                    ('palatino', 'Palatino Linotype'),
                    ('book_antiqua', 'Book Antiqua'),
                    ('cambria', 'Cambria'),
                    ('arial', 'Arial'),
                    ('calibri', 'Calibri'),
                    ('verdana', 'Verdana'),
                    ('tahoma', 'Tahoma'),
                    ('trebuchet', 'Trebuchet MS'),
                    ('segoe', 'Segoe UI'),
                    ('century_gothic', 'Century Gothic'),
                    ('helvetica', 'Helvetica'),
                    ('ubuntu', 'Ubuntu'),
                    ('droid_sans', 'Droid Sans'),
                    ('liberation_sans', 'Liberation Sans'),
                    ('courier', 'Courier New'),
                    ('consolas', 'Consolas'),
                    ('comic_sans', 'Comic Sans MS'),
                    ('noto_nastaliq', 'Noto Nastaliq Urdu'),
                    ('noto_naskh', 'Noto Naskh Arabic'),
                    ('segoe_urdu', 'Segoe UI (Urdu)'),
                ],
                default='calibri',
                max_length=50
            ),
        ),
        migrations.AlterField(
            model_name='presentation',
            name='heading_font',
            field=models.CharField(
                choices=[
                    ('georgia', 'Georgia'),
                    ('times', 'Times New Roman'),
                    ('garamond', 'Garamond'),
                    ('palatino', 'Palatino Linotype'),
                    ('book_antiqua', 'Book Antiqua'),
                    ('cambria', 'Cambria'),
                    ('arial', 'Arial'),
                    ('calibri', 'Calibri'),
                    ('verdana', 'Verdana'),
                    ('tahoma', 'Tahoma'),
                    ('trebuchet', 'Trebuchet MS'),
                    ('segoe', 'Segoe UI'),
                    ('century_gothic', 'Century Gothic'),
                    ('helvetica', 'Helvetica'),
                    ('ubuntu', 'Ubuntu'),
                    ('droid_sans', 'Droid Sans'),
                    ('liberation_sans', 'Liberation Sans'),
                    ('courier', 'Courier New'),
                    ('consolas', 'Consolas'),
                    ('comic_sans', 'Comic Sans MS'),
                    ('noto_nastaliq', 'Noto Nastaliq Urdu'),
                    ('noto_naskh', 'Noto Naskh Arabic'),
                    ('segoe_urdu', 'Segoe UI (Urdu)'),
                ],
                default='calibri',
                max_length=50
            ),
        ),
        migrations.AlterField(
            model_name='presentation',
            name='content_font',
            field=models.CharField(
                choices=[
                    ('georgia', 'Georgia'),
                    ('times', 'Times New Roman'),
                    ('garamond', 'Garamond'),
                    ('palatino', 'Palatino Linotype'),
                    ('book_antiqua', 'Book Antiqua'),
                    ('cambria', 'Cambria'),
                    ('arial', 'Arial'),
                    ('calibri', 'Calibri'),
                    ('verdana', 'Verdana'),
                    ('tahoma', 'Tahoma'),
                    ('trebuchet', 'Trebuchet MS'),
                    ('segoe', 'Segoe UI'),
                    ('century_gothic', 'Century Gothic'),
                    ('helvetica', 'Helvetica'),
                    ('ubuntu', 'Ubuntu'),
                    ('droid_sans', 'Droid Sans'),
                    ('liberation_sans', 'Liberation Sans'),
                    ('courier', 'Courier New'),
                    ('consolas', 'Consolas'),
                    ('comic_sans', 'Comic Sans MS'),
                    ('noto_nastaliq', 'Noto Nastaliq Urdu'),
                    ('noto_naskh', 'Noto Naskh Arabic'),
                    ('segoe_urdu', 'Segoe UI (Urdu)'),
                ],
                default='arial',
                max_length=50
            ),
        ),
    ]
