# Generic Knights

Autor: **ZeroDS** · [Código-fonte e releases](https://github.com/andersongz0/GenericKnights)

Versão publicada: **0.1.25-art-test**, conservando o conteúdo da última versão
testada. Adiciona classes genéricas masculinas e femininas:

- Holy Knight: Holy Sword; Knight 8 + White Mage 8.
- Rune Knight: Limit; Knight 8 + Time Mage 8.

Inclui sprites enhanced Scale2x, retratos e recursos de seleção de classe.
Os SPR de fallback e suas paletas são preservados.

## Dependências e instalação

Instale primeiro [FFTModLoader 0.11.6](https://github.com/andersongz0/FFTModLoader/releases).
Generic Knights declara `fftivc.utility.modloader` e usa o **JobExpansion
0.2.7 integrado** para as classes e recursos extras. Na configuração atual,
JobExpansion também requer GenericJobs original, SigScan e SharedLib.Hooks;
essas dependências já acompanham o pacote do FFTModLoader.

**Não depende de Reworked Chemist.** Os IDs e arquivos das dependências de
terceiros devem permanecer intactos.

Extraia `GenericKnights-0.1.25.zip` separadamente. Com jogo e loader fechados,
execute `install.ps1 -GameDirectory "caminho da pasta do jogo"`. Ele instala
`Mods/Generic Knights` com backup recuperável e não altera saves.

Veja [BUILD.md](BUILD.md) e [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
