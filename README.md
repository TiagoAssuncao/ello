# Processo seletivo Ello

Aqui será apresentado o manual de instalação e usabilidade.

## Instalação
Para este MVP, foi utilizado python e Django. Assim, caso não tenha o python instalado, instale a versão 3.5.

Para instalar as dependências, utilize o seguinte comando no seu ambiente virtual:

`pip install -r requeriments.txt`

## Utilização

Para iniciar o código, basta apenas gerar as migrates, criar o banco e rodar o comando do shell que faz
o parser dos dados.

Assim, execute os seguintes comandos, que irão apagar o banco caso exista(para fins de demonstração de execução correta) e criar um novo:

```
rm db.sqlite3; rm senadores/migrations/00*; ./manage.py makemigrations; ./manage.py migrate;

./manage.py parser

```
