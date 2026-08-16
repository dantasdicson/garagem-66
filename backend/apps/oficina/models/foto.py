from django.db import models


class Foto(models.Model):
    entrada_veiculo = models.ForeignKey("oficina.EntradaVeiculo", on_delete=models.CASCADE, related_name="fotos")
    imagem = models.ImageField(upload_to="entradas/fotos/")
    descricao = models.CharField(max_length=255, blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "foto"
        verbose_name_plural = "fotos"
