from django.db import migrations


def crear_grupos(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')

    grupos = ['Transporte', 'Directivo', 'Petroleo', 'Almacen', 'Random']

    for nombre in grupos:
        Group.objects.get_or_create(name=nombre)


def eliminar_grupos(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=['Transporte', 'Directivo', 'Petroleo', 'Almacen', 'Random']).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(crear_grupos, eliminar_grupos),
    ]