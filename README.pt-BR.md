# Generic Knights

[English](README.md) | [Português](README.pt-BR.md)

Autor do mod: **ZeroDS** · [Código-fonte e releases](https://github.com/andersongz0/GenericKnights)

**0.1.26-rc.1** atualiza documentação e créditos. Dados de gameplay, texturas Scale2x,
sprites de fallback e paletas permanecem iguais à versão aprovada **0.1.25-art-test**.

- Holy Knight masculino/feminino: Holy Sword; Knight 8 + White Mage 8.
- Rune Knight masculino/feminino: Limit; Knight 8 + Time Mage 8.

## Instalação e dependências

Instale primeiro [FFTModLoader 0.11.7-rc.1](https://github.com/andersongz0/FFTModLoader/releases).
Extraia **GenericKnights-0.1.26-rc.1.zip** fora da pasta do jogo e execute
`install.ps1 -GameDirectory "pasta do jogo"` com jogo/loader fechados.
Abra FFTModLoader.exe no modo Enhanced.

Requer Utility Mod Loader e JobExpansion integrado. GenericJobs original, SigScan e SharedLib.Hooks,
dependências do JobExpansion, já acompanham FFTModLoader.
**Não depende de Reworked Chemist.** Saves e outros mods são preservados.

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
