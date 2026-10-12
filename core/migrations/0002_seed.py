from django.db import migrations

from core.starter_data import ACHIEVEMENTS, PROJECTS


def seed(apps, schema_editor):
    Project = apps.get_model("core", "Project")
    Achievement = apps.get_model("core", "Achievement")
    if not Project.objects.exists():
        field_names = {f.name for f in Project._meta.fields}
        Project.objects.bulk_create([
            Project(**{k: v for k, v in p.items() if k in field_names})
            for p in PROJECTS
        ])
    if not Achievement.objects.exists():
        field_names_a = {f.name for f in Achievement._meta.fields}
        Achievement.objects.bulk_create([
            Achievement(**{k: v for k, v in a.items() if k in field_names_a})
            for a in ACHIEVEMENTS
        ])


class Migration(migrations.Migration):
    dependencies = [("core", "0001_initial")]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
