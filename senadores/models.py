from django.db import models


class UfParlamentar(models.Model):
    uf_parlamentar = models.CharField(max_length=2, unique=True)


class SiglaPartidoParlamentar(models.Model):
    sigla_parlamentar = models.CharField(max_length=10, unique=True)


class IdentificacaoParlamentar(models.Model):
    SEXO = (
        ('M', 'Masculino'),
        ('F', 'Feminino'),
    )

    TRATAMENTO = (
        ('M', 'Senador'),
        ('F', 'Senadora'),
    )

    codigo_parlamentar = models.PositiveSmallIntegerField(unique=True)
    nome_parlamentar = models.CharField(max_length=100, unique=True)
    nome_completo_parlamentar = models.CharField(max_length=200, unique=True)
    sexo_parlamentar = models.CharField(max_length=1, choices=SEXO)
    forma_tratamento = models.CharField(max_length=1, choices=TRATAMENTO)
    url_foto_parlamentar = models.URLField(unique=True)
    url_pagina_parlamentar = models.URLField(unique=True)
    email_parlamentar = models.EmailField()

    sigla_partido_parlamentar = models.ForeignKey(
        SiglaPartidoParlamentar,
        on_delete=models.DO_NOTHING
    )

    uf_parlamentar = models.ForeignKey(
        UfParlamentar,
        on_delete=models.DO_NOTHING
    )


class LegislaturaMandato(models.Model):
    data_inicio = models.DateField()
    data_fim = models.DateField()
    numero_legislatura = models.PositiveSmallIntegerField(unique=True)


class DescricaoParticipacao(models.Model):
    descricao = models.CharField(max_length=50, unique=True)


class Mandato(models.Model):
    codigo_mandato = models.PositiveSmallIntegerField(unique=True)
    descricao_participacao = models.ForeignKey(
        DescricaoParticipacao,
        on_delete=models.DO_NOTHING
    )

    primeira_legislatura = models.ForeignKey(
        LegislaturaMandato,
        related_name="primeira_legislatura",
        on_delete=models.DO_NOTHING
    )

    segunda_legislatura = models.ForeignKey(
        LegislaturaMandato,
        related_name="segunda_legislatura",
        on_delete=models.DO_NOTHING
    )

    uf_parlamentar = models.ForeignKey(
        UfParlamentar,
        on_delete=models.DO_NOTHING
    )


class Parlamentar(models.Model):
    identificacao_parlamentar = models.OneToOneField(
        IdentificacaoParlamentar,
        on_delete=models.CASCADE
    )

    mandato = models.OneToOneField(
        Mandato,
        on_delete=models.CASCADE
    )

    url_glossario = models.URLField()


class Suplente(models.Model):
    codigo_parlamentar = models.PositiveSmallIntegerField(unique=True)
    nome_parlamentar = models.CharField(max_length=200)

    descricao_participacao = models.ForeignKey(
        DescricaoParticipacao,
        on_delete=models.DO_NOTHING
    )

    mandato = models.ForeignKey(
        Mandato,
        on_delete=models.DO_NOTHING
    )


class Exercicio(models.Model):
    codigo_exercicio = models.PositiveSmallIntegerField(unique=True)
    data_inicio = models.DateField()
    data_fim = models.DateField(blank=True, null=True)
    data_leitura = models.DateField(blank=True, null=True)

    descricao_causa_afastamento = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    sigla_causa_afastamento = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    mandato = models.ForeignKey(
        Mandato,
        on_delete=models.DO_NOTHING
    )
