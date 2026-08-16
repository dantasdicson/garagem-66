from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("oficina", "0006_historicostatusordem")]
    operations = [
        migrations.CreateModel(
            name="ModeloMotocicleta",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("marca", models.CharField(max_length=80)),
                ("modelo", models.CharField(max_length=120)),
                ("categoria", models.CharField(choices=[("TRAIL", "Trail"), ("BIG_TRAIL", "Big trail / Adventure")], max_length=20)),
                ("ativo", models.BooleanField(default=True)),
                ("fonte_url", models.URLField(blank=True)),
            ],
            options={"ordering": ("marca", "modelo")},
        ),
        migrations.AddConstraint(
            model_name="modelomotocicleta",
            constraint=models.UniqueConstraint(fields=("marca", "modelo"), name="modelo_moto_marca_modelo_unico"),
        ),
    ]
