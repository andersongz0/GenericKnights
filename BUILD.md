# Fontes e recursos

O diretório `GenericKnights` preserva os geradores, o conversor de sprites e
as entradas de arte das revisões v5/v6. `art-v6/Mod` é o pacote de dados final.
Não contém executável próprio: o roteamento das classes é feito pelo JobExpansion.

`build_tables.py` espera tabelas originais extraídas da sua instalação em
`GenericKnights/analysis/base-tables.sqlite`. Elas não são distribuídas.
Use FF16Tools para extrair/converter seus dados legalmente; configure seu
caminho em `FF16TOOLS_CLI` para `rebuild_mod.py`.

As fontes SPR, os BMPs próprios, os índices Scale2x e os retratos selecionados
estão incluídos. `build_filtered_art.py` preserva os SPR e transforma os índices
em páginas e atlas. As comparações históricas esperam recursos de referência
da sua própria instalação e FF16Tools em `FF16 Tools/win-x64`, junto da pasta
`GenericKnights`. Os testes de textura exigem o executor `dds-preview` (.NET 9).

O runner `toolkit-filter-runner` é um adaptador para o Sprite Modding Toolkit.
Ele espera `ImageProcessor.cs` e `UpscaleMethod.cs` do Toolkit, obtidos pelo
usuário, no local indicado pelo projeto. O código de terceiros descompilado
do Toolkit **não é redistribuído**. Os resultados selecionados necessários ao
pacote final já estão em `art-v6/filters/Scale2x` e `art-v6/portraits/Scale2x`.

Instale Python 3 com Pillow e SDK .NET 9 para as ferramentas gerenciadas.
Os scripts históricos podem solicitar recursos externos específicos; não
confunda uma pasta de referência extraída do jogo com código-fonte do mod.
