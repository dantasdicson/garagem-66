from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("oficina", "0007_modelomotocicleta"),
    ]

    operations = [
        migrations.AlterField(
            model_name="orcamento",
            name="status",
            field=models.CharField(
                choices=[
                    ("RASCUNHO", "Rascunho aguardando publicação"),
                    ("AGUARDANDO_APROVACAO", "Aguardando aprovação"),
                    ("APROVADO", "Aprovado"),
                    ("RECUSADO", "Recusado"),
                ],
                default="RASCUNHO",
                max_length=25,
            ),
        ),
        migrations.AddField(
            model_name="orcamento",
            name="publicado_em",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="orcamento",
            name="publicado_por",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="orcamentos_publicados",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
