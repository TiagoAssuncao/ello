import requests as api
import datetime
import pprint
from senadores.models import (
    IdentificacaoParlamentar,
    Parlamentar,
    UfParlamentar,
    Mandato,
    DescricaoParticipacao,
    LegislaturaMandato,
    Exercicio,
    Suplente,
    SiglaPartidoParlamentar
)
from django.core.management.base import BaseCommand, CommandError


def make_suplente(suplente_json, mandato):
    descricao, _ = DescricaoParticipacao.objects.get_or_create(
        descricao=suplente_json['DescricaoParticipacao']
    )

    suplente, _ = Suplente.objects.get_or_create(
        codigo_parlamentar=int(suplente_json['CodigoParlamentar']),
        nome_parlamentar=suplente_json['NomeParlamentar'],
        descricao_participacao=descricao,
        mandato=mandato
    )


def make_exercicio(exercicio_json, mandato):
    if 'DataInicio' in exercicio_json.keys():
        data_inicio = datetime.datetime.strptime(
            exercicio_json['DataInicio'], '%Y-%m-%d')
    else:
        data_inicio = None

    if 'DataFim' in exercicio_json.keys():
        data_fim = datetime.datetime.strptime(
            exercicio_json['DataFim'], '%Y-%m-%d')
    else:
        data_fim = None

    if 'DataLeitura' in exercicio_json.keys():
        data_leitura = datetime.datetime.strptime(
            exercicio_json['DataLeitura'], '%Y-%m-%d')
    else:
        data_leitura = None

    if 'DescricaoCausaAfastamento' in exercicio_json.keys():
        descricao_causa_afastamento = exercicio_json['DescricaoCausaAfastamento']
    else:
        descricao_causa_afastamento = None

    if 'SiglaCausaAfastamento' in exercicio_json.keys():
        sigla_causa_afastamento = exercicio_json['SiglaCausaAfastamento']
    else:
        sigla_causa_afastamento = None

    exercicio, _ = Exercicio.objects.get_or_create(
        codigo_exercicio=int(exercicio_json['CodigoExercicio']),
        data_inicio=data_inicio,
        data_fim=data_fim,
        data_leitura=data_leitura,
        descricao_causa_afastamento=descricao_causa_afastamento,
        sigla_causa_afastamento=sigla_causa_afastamento,
        mandato=mandato
    )


def make_mandato(mandato_json):
    descricao, _ = DescricaoParticipacao.objects.get_or_create(
        descricao=mandato_json['DescricaoParticipacao']
    )

    data_inicio = datetime.datetime.strptime(
        mandato_json['PrimeiraLegislaturaDoMandato']['DataInicio'], '%Y-%m-%d')
    data_fim = datetime.datetime.strptime(
        mandato_json['PrimeiraLegislaturaDoMandato']['DataFim'], '%Y-%m-%d')

    primeira_legislatura, _ = LegislaturaMandato.objects.get_or_create(
        data_inicio=data_inicio, data_fim=data_fim, numero_legislatura=int(
            mandato_json['PrimeiraLegislaturaDoMandato']['NumeroLegislatura']))

    data_inicio = datetime.datetime.strptime(
        mandato_json['SegundaLegislaturaDoMandato']['DataInicio'], '%Y-%m-%d')
    data_fim = datetime.datetime.strptime(
        mandato_json['SegundaLegislaturaDoMandato']['DataFim'], '%Y-%m-%d')

    segunda_legislatura, _ = LegislaturaMandato.objects.get_or_create(
        data_inicio=data_inicio, data_fim=data_fim, numero_legislatura=int(
            mandato_json['SegundaLegislaturaDoMandato']['NumeroLegislatura']))

    uf, _ = UfParlamentar.objects.get_or_create(
        uf_parlamentar=mandato_json['UfParlamentar']
    )

    mandato = Mandato(
        codigo_mandato=int(mandato_json['CodigoMandato']),
        descricao_participacao=descricao,
        primeira_legislatura=primeira_legislatura,
        segunda_legislatura=segunda_legislatura,
        uf_parlamentar=uf
    )
    mandato.save()

    if isinstance(mandato_json['Exercicios']['Exercicio'], list):
        for exercicio_json in mandato_json['Exercicios']['Exercicio']:
            make_exercicio(exercicio_json, mandato)
    else:
        make_exercicio(mandato_json['Exercicios']['Exercicio'], mandato)

    if isinstance(mandato_json['Suplentes']['Suplente'], list):
        for suplente_json in mandato_json['Suplentes']['Suplente']:
            make_suplente(suplente_json, mandato)
    else:
        make_suplente(mandato_json['Suplentes']['Suplente'], mandato)

    return mandato


def make_identificao(parlamentar):
    identificao = parlamentar['IdentificacaoParlamentar']

    uf, _ = UfParlamentar.objects.get_or_create(
        uf_parlamentar=identificao['UfParlamentar']
    )

    sigla, _ = SiglaPartidoParlamentar.objects.get_or_create(
        sigla_parlamentar=identificao['SiglaPartidoParlamentar']
    )

    email = identificao['EmailParlamentar'] if 'EmailParlamentar' in identificao.keys(
    ) else ''

    identificacao_parlamentar, created = IdentificacaoParlamentar.objects.get_or_create(
        codigo_parlamentar=int(identificao['CodigoParlamentar']),
        nome_parlamentar=identificao['NomeParlamentar'],
        nome_completo_parlamentar=identificao['NomeCompletoParlamentar'],
        sexo_parlamentar=identificao['SexoParlamentar'],
        forma_tratamento=identificao['FormaTratamento'],
        url_foto_parlamentar=identificao['UrlFotoParlamentar'],
        url_pagina_parlamentar=identificao['UrlPaginaParlamentar'],
        email_parlamentar=email,
        sigla_partido_parlamentar=sigla,
        uf_parlamentar=uf
    )

    return identificacao_parlamentar, created


def parser_parlamentar():
    headers = {
        'Content-type': 'application/json',
        'Accept': 'application/json'}
    response = api.get(
        'http://legis.senado.gov.br/dadosabertos/senador/lista/atual',
        headers=headers)
    parlamentares = response.json(
    )['ListaParlamentarEmExercicio']['Parlamentares']['Parlamentar']

    counter = 0

    for parlamentar in parlamentares:
        identificacao_parlamentar, created = make_identificao(parlamentar)

        if created:
            pprint.pprint(parlamentar)
            counter += 1
            mandato = make_mandato(parlamentar['Mandato'])
            parlamentar_obj = Parlamentar.objects.create(
                identificacao_parlamentar=identificacao_parlamentar,
                mandato=mandato,
                url_glossario=parlamentar['UrlGlossario']
            )

    return counter


class Command(BaseCommand):
    help = 'Captura os parlamentares para a base de dados'

    def handle(self, *args, **options):
        counter = parser_parlamentar()
        self.stdout.write(
            self.style.SUCCESS(
                "{} Parlamentares cadastrados com sucesso!!".format(counter)))
