from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    atomic = False

    operations = [
        migrations.RunSQL(
            sql="PRAGMA journal_mode=WAL; PRAGMA synchronous=normal; PRAGMA busy_timeout=5000; PRAGMA foreign_keys=ON;",
            reverse_sql="PRAGMA journal_mode=DELETE; PRAGMA synchronous=FULL; PRAGMA busy_timeout=0; PRAGMA foreign_keys=OFF;",
        ),
    ]
