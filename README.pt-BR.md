# Generic Knights

[English](README.md) | [Português](README.pt-BR.md)

Autor: **ZeroDS** · [Código-fonte e releases](https://github.com/andersongz0/GenericKnights)

Generic Knights adiciona **Holy Knight** e **Rune Knight** como classes para unidades genéricas masculinas e femininas, com sprites de batalha, retratos de menu e comandos próprios.

## Funcionalidades

- Holy Knight masculino/feminino: Holy Sword; Knight 8 + White Mage 8.
- Rune Knight masculino/feminino: Limit; Knight 8 + Time Mage 8.

## Requisitos

- Windows x64 e instalação legítima de **FINAL FANTASY TACTICS - The Ivalice Chronicles** pela Steam, modo Enhanced.
- [FFTModLoader 0.11.7-rc.2](https://github.com/andersongz0/FFTModLoader/releases/tag/v0.11.7-rc.2), instalado com o pacote completo.

JobExpansion, Utility Mod Loader e suas dependências de compatibilidade acompanham o FFTModLoader.

## Guia de Instalação do Generic Knights

1. Instale FFTModLoader seguindo [o guia dele](https://github.com/andersongz0/FFTModLoader/blob/main/README.pt-BR.md#guia-de-instalação-do-fftmodloader).
2. Feche o jogo. Feche também o loader, caso já esteja instalado e aberto.
3. Baixe **GenericKnights-0.1.26-rc.2.zip** em [Assets da release](https://github.com/andersongz0/GenericKnights/releases/tag/v0.1.26-rc.2), não **Source code**.
4. Extraia o ZIP em uma pasta separada, fora da instalação do jogo.
5. Dê dois cliques em **Install.cmd** e escolha o idioma.
6. Confira a pasta encontrada e digite **SIM** para confirmar. Se houver várias instalações, escolha uma; se nenhuma for encontrada, informe o caminho de **FFT_enhanced.exe** ou da pasta que o contém.
7. Autorize a solicitação de permissão do Windows, se aparecer, e aguarde a mensagem de conclusão.

Não é necessário digitar comandos. O instalador verifica o pacote e guarda arquivos substituídos em **FFTModLoader.Backup**, dentro da pasta do jogo. Saves e outros mods são preservados.
O mod é instalado em **Mods/Generic Knights**.

## Como usar

Abra **FFTModLoader.exe** na pasta do jogo. Alcance os níveis de classes informados acima para liberar as novas classes nas unidades genéricas.

## Atualização

Feche o jogo e o loader, se estiver aberto, e execute **Install.cmd** da nova release completa. Se faltarem arquivos de dependências, reinstale o pacote completo do FFTModLoader.

## Créditos dos sprites

O [catálogo FFHacktics](https://ffhacktics.com/sprites.php) identifica os autores abaixo.
Rune Knight usa a arte catalogada como **Rogue**, renomeada para sua função neste mod.

| Arte no mod | Entrada no catálogo | Sprite | Retrato | Paletas |
| --- | --- | --- | --- | --- |
| Holy Knight masculino | Male Paladin | Lijj | Lijj | Lijj |
| Holy Knight feminino | Female Paladin | Lijj | Twinees | Lijj |
| Rune Knight masculino | Male Rogue | R999 | Lijj | Lijj |
| Rune Knight feminino | Female Rogue | R999 | Lijj | Lijj |

ZeroDS fez a integração e conversão do mod, sem assumir a autoria original dos sprites/retratos.
[SPRITE_CREDITS.json](SPRITE_CREDITS.json) registra hashes dos arquivos e a evidência da atribuição.
A arte não é relicenciada como código original de ZeroDS.

**Nenkai**: Utility Mod Loader, FF16Tools e FaithFramework.
**Kanaruu**: FFT Ivalice Chronicles - Sprite Modding Toolkit, usado nas comparações de filtros e resultados Scale2x escolhidos.
**cipherxof**: FFTGenericJobs original, base de compatibilidade; o aviso MIT preservado credita trigger.

Veja [créditos/ferramentas](CREDITS.pt-BR.md), [compilação](BUILD.pt-BR.md) e [avisos de terceiros](THIRD_PARTY_NOTICES.md).
