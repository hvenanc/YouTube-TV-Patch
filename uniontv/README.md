# UnionTV — YouTube TV 5.30.340

[Voltar ao projeto](../README.md)

Patch experimental, específico para o **YouTube TV 5.30.340 ARMv7**, preparado a partir dos APKs extraídos de uma UnionTV com Android 9 (API 28).

**Estado atual: revisão r4, com verificações locais concluídas e validação na TV pendente.** Ainda não há confirmação de bloqueio confiável de anúncios no início, durante vídeos ou em lives.

## O que faz

- Filtra campos de anúncios em dados processados por `JSON.parse`.
- Tenta acrescentar `isInlinePlaybackNoAd: true` em solicitações com `playbackContext.contentPlaybackContext` compatível. O servidor pode ignorar esse campo.
- Mantém os limites dos quatro scripts embutidos do Cobalt; modifica apenas os blocos de streams e fetch.
- Encaminha uma recusa específica de verificação GMS ao callback de falha, evitando relançar essa exceção. Não autoriza o acesso ao serviço recusado.
- Reúne as bibliotecas ARMv7 em um APK único, com outro identificador de pacote.

Não inclui SponsorBlock. Login Google, Cast e outras integrações dependentes da assinatura oficial podem não funcionar.

## Compatibilidade

| Item | Base analisada |
| --- | --- |
| Aplicativo | YouTube para Android TV 5.30.340 |
| Version code | `530340320` |
| Pacote original | `com.google.android.youtube.tv` |
| Pacote gerado | `local.youtubetv.uniontv` |
| Arquitetura | `armeabi-v7a` |
| Android mínimo declarado | API 24, preservada do original |
| Aparelho de referência | UnionTV, Android 9 / API 28 |

Os scripts verificam hashes da base e da biblioteca. **Não são um patch genérico para outras versões.** A variante TCL com YouTube 7.27.302 está em [../tcl/](../tcl/README.md), com outra estratégia de injeção.

## Compilar

Este diretório contém somente código próprio de adaptação, testes e documentação. Forneça os APKs originais e as ferramentas no seu ambiente; os scripts de inicialização derivados do Cobalt são gerados localmente.

1. Instale Java, Python 3, Node.js e `unzip`.
2. Obtenha o Apktool 2.12.1 e o Uber APK Signer 1.3.0.
3. Coloque os APKs compatíveis em `input/` e os JARs em `tools/`.
4. Siga [Compilação e instalação](docs/BUILD.md), incluindo a geração e a verificação dos quatro blocos antes do empacotamento.

Ambiente usado nas verificações: Java 21, Python 3.12 e Node.js 24.18.0. O minificador é fixado em Terser 5.44.0 pelo lockfile.

## Diagnóstico da r4

O nome gerado é **YouTube TV UnionTV r4**, com versão de manifesto `5.30.340-r4`. Na primeira chamada de `JSON.parse` em que o DOM esteja disponível, a revisão tenta exibir uma borda vermelha de 8 px durante 10 segundos.

A borda é um diagnóstico temporário: sua presença mostra que o hook executou e conseguiu modificar o DOM. Sua ausência, isoladamente, não identifica a causa. O diagnóstico não depende de `console.warn`.

Veja [Testes e diagnóstico](docs/TESTING.md) para registrar resultados no aparelho.

## Limites e estado das revisões

Anúncios em dados não interceptados, mudanças no servidor e anúncios integrados ao fluxo podem escapar da filtragem. Testes em Node.js não substituem testes em Cobalt/Android.

As revisões r1–r3 foram invalidadas por um erro de empacotamento: quatro scripts contíguos foram tratados como um único programa. A r4 corrige seus limites e o modelo de teste. Os relatos anteriores de redução de anúncios não comprovam a eficácia daquelas revisões. Consulte o [histórico](docs/CHANGELOG.md).

## Estrutura

```text
src/                  Hooks, gerador, patch Python e verificador
docs/BUILD.md         Preparação, compilação, assinatura e instalação
docs/ARCHITECTURE.md  Formato dos blocos e alterações aplicadas
docs/TESTING.md       Evidências locais e validação pendente na TV
docs/CHANGELOG.md     Histórico das revisões
docs/REFERENCES.md    Referências e componentes externos
```

`input/`, `tools/`, `build/`, `dist/` e o payload gerado são locais e ignorados pelo Git. APKs, bibliotecas, logs e chaves também são ignorados. Esta pasta não contém os binários nem os registros do aparelho usado no desenvolvimento.

## Relatar um problema

Informe revisão, versão/API do Android, arquitetura, versão da base, se o app instala/abre e se o anúncio aparece no início, durante o vídeo ou em uma live. Inclua os horários do evento e apenas o trecho relevante do log, sem dados de conta.

Este projeto não é afiliado ao YouTube, Google, Cobalt, Morphe ou TizenTube. As referências técnicas estão em [REFERENCES.md](docs/REFERENCES.md).

## Licença

A licença do código próprio ainda não foi definida. Este pacote não contém um arquivo `LICENSE`; as licenças dos componentes externos continuam aplicáveis a eles.
