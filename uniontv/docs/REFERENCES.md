# Referências e componentes externos

## Cobalt

A base analisada contém identificação Cobalt `25.lts.30`. Os arquivos abaixo, do ramo histórico 25, serviram de referência para o carregamento dos arrays. Não representam uma garantia de correspondência integral entre o binário proprietário e o código público.

- [EvaluateAutomatics e EvaluateEmbeddedScript](https://github.com/youtube/cobalt/blob/b79ea7d011b2e9392109a4668fe8130fcf7d2d6e/cobalt/script/v8c/v8c_global_environment.cc)
- [Geração de arrays com tamanho dos arquivos](https://github.com/youtube/cobalt/blob/b79ea7d011b2e9392109a4668fe8130fcf7d2d6e/cobalt/build/generate_data_header.py)
- [Lista dos recursos embutidos](https://github.com/youtube/cobalt/blob/b79ea7d011b2e9392109a4668fe8130fcf7d2d6e/cobalt/script/v8c/BUILD.gn)

Os scripts embutidos são extraídos do APK fornecido localmente, transformados e usados no empacotamento. O payload resultante e as bibliotecas não são incluídos neste repositório. Componentes externos mantêm suas respectivas licenças; o projeto não atribui uma licença própria a esses componentes.

## Filtragem e campo de reprodução

- [TizenTube — módulo adblock](https://github.com/reisxd/TizenTube/blob/main/mods/features/adblock.js): referência técnica para os campos de anúncio e a opção `isInlinePlaybackNoAd`.

Este projeto não inclui o aplicativo ou o módulo completo do TizenTube. A tentativa de enviar esse campo não garante que o servidor respeite a opção.

## Ferramentas

- [Apktool 2.12.1](https://github.com/iBotPeaches/Apktool/releases/tag/v2.12.1)
- [Uber APK Signer 1.3.0](https://github.com/patrickfav/uber-apk-signer/releases/tag/v1.3.0)
- [Terser](https://github.com/terser/terser), versão 5.44.0 fixada no lockfile
- [Acorn](https://github.com/acornjs/acorn), dependência transitiva do Terser usada para analisar os scripts

Os JARs não são fornecidos neste repositório. Dependências npm são obtidas com `npm ci`.
