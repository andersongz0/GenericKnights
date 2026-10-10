# Compilar Generic Knights

[English](BUILD.md) | [Português](BUILD.pt-BR.md)

`GenericKnights` contém geradores, conversor, SPR originais creditados,
índices/retratos Scale2x escolhidos e dados finais em `art-v6/Mod`.
Não há DLL de gameplay própria: JobExpansion fornece o roteamento.

Use Python 3 com Pillow e SDK .NET 9 nas ferramentas.
`build_tables.py` requer tabelas extraídas da sua instalação em `analysis/base-tables.sqlite`, não distribuídas.
Use FF16Tools de Nenkai e informe `FF16TOOLS_CLI` a `rebuild_mod.py`.

`build_filtered_art.py` preserva os SPR de fallback e converte os índices selecionados em páginas/atlas.
Comparações históricas exigem recursos legítimos da instalação e FF16Tools.
`toolkit-filter-runner` usa `ImageProcessor.cs`/`UpscaleMethod.cs` do Toolkit de Kanaruu fornecidos localmente.
Código descompilado não é redistribuído. Os resultados finais escolhidos já acompanham as fontes.
Visualizações DDS usam `dds-preview` e suas dependências externas.

Autores originais constam no README e em SPRITE_CREDITS.json.
Os créditos não concedem uma licença geral sobre a arte de terceiros.
`FFTModLoader.jobs.json` ativa a rota nativa de espada do JobExpansion para o comando 163.
O resumo do Rune Knight usa uma linha própria, 163; a linha original 31 do Cloud é preservada.
A atualização rc.4 exige FFTModLoader rc.9. Arte, requisitos de liberação e dados das habilidades permanecem intactos.
