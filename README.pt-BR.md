# Generic Knights

[English](README.md) | [Português](README.pt-BR.md)

Autor do mod: **ZeroDS** · [Código-fonte e releases](https://github.com/andersongz0/GenericKnights)

**0.1.26-rc.1** atualiza documentação e créditos. Dados de gameplay, texturas Scale2x,
sprites de fallback e paletas permanecem iguais à versão aprovada **0.1.25**.

- Holy Knight masculino/feminino: Holy Sword; Knight 8 + White Mage 8.
- Rune Knight masculino/feminino: Limit; Knight 8 + Time Mage 8.

## Requisitos

- Windows x64 e instalação legítima da Steam de **FINAL FANTASY TACTICS - The Ivalice Chronicles**, modo Enhanced.
- [FFTModLoader 0.11.7-rc.1](https://github.com/andersongz0/FFTModLoader/releases/tag/v0.11.7-rc.1), instalado com o pacote completo.
- Utility Mod Loader e **JobExpansion** integrado. GenericJobs original, SigScan e SharedLib.Hooks são dependências de compatibilidade desses componentes.

Todos os componentes necessários acompanham FFTModLoader; não é necessário baixar dependências separadamente.

## Guia de Instalação do Generic Knights

1. Instale FFTModLoader seguindo [o guia dele](https://github.com/andersongz0/FFTModLoader/blob/main/README.pt-BR.md#guia-de-instalação-do-fftmodloader).
2. Feche o jogo e o loader.
3. Baixe **GenericKnights-0.1.26-rc.1.zip** em [Assets da release](https://github.com/andersongz0/GenericKnights/releases/tag/v0.1.26-rc.1), não **Source code**.
4. Extraia fora da pasta do jogo. Abra o PowerShell na pasta extraída e execute `./install.ps1 -GameDirectory "pasta do jogo"`.
5. Confira se **Mods/Generic Knights/ModConfig.json** existe na instalação do jogo.
6. Abra **FFTModLoader.exe** no modo Enhanced. Alcance os níveis de classes informados acima para liberar as novas classes.

O instalador confere hashes e guarda arquivos substituídos em **FFTModLoader.Backup**. Saves e outros mods são preservados.
Para atualizar, feche jogo/loader e instale a nova release completa. Mantenha apenas uma cópia ativa de Generic Knights.
Se faltarem dependências, reinstale o pacote completo do FFTModLoader.

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
Novos mods só são publicados após o usuário decidir que estão finalizados.
