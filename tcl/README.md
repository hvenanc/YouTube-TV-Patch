# TCL — YouTube TV 7.27.302

[Voltar ao projeto](../README.md)

Variante local v3 cujo funcionamento foi confirmado pelo usuário na **TCL 50P7K, Android TV 12**, com atualização de segurança informada de 5 de dezembro de 2025. A confirmação foi “Funcionou”; não houve validação detalhada de todos os formatos de anúncios, login ou Cast.

Pacote: `local.youtubetv.experimental`. Arquitetura: `armeabi-v7a`. O mínimo declarado foi reduzido de API 32 para API 31, sem garantia de compatibilidade com outros aparelhos.

Este diretório de publicação contém apenas os quatro fontes em `src/` e esta documentação. Os APKs, o APKM original, as ferramentas e os logs ficam no ambiente local.

O APK validado foi renomeado para `YouTube-TV-7.27.302.apk`, mas seu nome interno permanece **YouTube TV - Teste v3**. Os comandos abaixo preservam esse nome para reproduzir a variante validada; uma alteração no nome interno exige nova compilação e nova validação.

## O que o patch faz

- Usa uma chamada JNI existente do Cobalt para executar um JavaScript local
  no conteúdo do YouTube quando a página principal é carregada.
- Filtra os arrays `adPlacements`, `playerAds`, `adSlots` e `adBreaks` em
  objetos JSON e nos dados iniciais acessíveis da página.
- Tenta acionar botões visíveis de pular anúncio, evitando cliques repetidos.
- Atua somente em `www.youtube.com` e `youtube.com`.
- Une as seis bibliotecas ARMv7 do split em um APK único.
- Trata a recusa GMS `PackageVerificationRslt: not allowed:` como falha de
  conexão com o serviço, em vez de relançar essa exceção e encerrar o app.

Essa última alteração preserva a recusa do Google: não modifica o pedido,
a assinatura apresentada nem a resposta do serviço. Outras mensagens de
`SecurityException` mantêm o comportamento original.

O patch não adiciona servidores, scripts remotos ou coleta de dados ao app
original. Não é um patch oficial do Morphe nem um arquivo importável no Manager.

## Limites conhecidos

Login Google, Cast e outras integrações dependentes do pacote ou da assinatura
oficial podem ficar indisponíveis. O APK usa uma assinatura de depuração.
Mudanças do YouTube no servidor podem afetar a filtragem e os botões de pular.
Anúncios em dados não interceptados ou integrados ao fluxo podem permanecer.

## Verificações realizadas

- Compilação do DEX e leitura do pacote com ferramentas Android.
- Integridade ZIP, alinhamento e assinatura v3 verificados.
- Recursos, assets e bibliotecas nativas comparados com os originais.
- Testes simulados do JavaScript para filtragem, preservação dos dados de
  vídeo, `JSON.parse` com reviver, restrição de host e prevenção de repetição.
- Nova decompilação do código GMS para conferir o tratamento da exceção.
- Confirmação de funcionamento pelo usuário na TCL informada.
- Comparação SHA-256 antes e depois de renomear o APK: conteúdo idêntico.

SHA-256 do APK:

```text
5dd984f9a9ccc78edd57a4f2ade153ba72a3ac75953a61983adc01016625c129
```

## Reproduzir a compilação

Requer Java, Python 3 e `unzip`. Obtenha Apktool 2.12.1 e Uber APK Signer 1.3.0 e coloque os JARs em `tools/`. Coloque o APKM original em `input/YouTube-TV-7.27.302-original.apkm`. Execute estes comandos a partir de `tcl/`.
Use uma pasta `build/` nova, sem alterações de uma execução anterior.

```bash
mkdir -p build/original
unzip input/YouTube-TV-7.27.302-original.apkm base.apk split_config.armeabi_v7a.apk -d build/original
java -jar tools/apktool.jar d -f -p build/framework -o build/decoded build/original/base.apk
python3 src/aplicar-patch.py build/decoded build/original/split_config.armeabi_v7a.apk
python3 src/corrigir-gms.py build/decoded
java -jar tools/apktool.jar b -p build/framework -o build/dex-source.apk build/decoded
python3 src/empacotar-v2.py input/YouTube-TV-7.27.302-original.apkm build/dex-source.apk build/unsigned.apk --api31 --label "YouTube TV - Teste v3"
java -jar tools/uber-apk-signer.jar --apks build/unsigned.apk --out build/signed
```

Apesar do nome `empacotar-v2.py`, esse script também é usado na v3. Ele preserva
os recursos originais e incorpora o DEX modificado. Os scripts são específicos
para o APKM 7.27.302 fornecido localmente; não foram validados para outras versões.

Os comandos usam o certificado de depuração embutido no Uber APK Signer,
usado no APK local validado. Para atualizar a instalação existente, a assinatura
precisa permanecer a mesma. Confira o certificado caso o computador tenha
outro keystore de depuração configurado. Uma nova compilação pode produzir
outro hash, mesmo preservando o comportamento do patch.

Ferramentas de origem:

- [Apktool 2.12.1](https://github.com/iBotPeaches/Apktool/releases/tag/v2.12.1)
- [Uber APK Signer 1.3.0](https://github.com/patrickfav/uber-apk-signer/releases/tag/v1.3.0)

## Diagnóstico e validação

Depois de assinar, instale o arquivo gerado em `build/signed/` com `adb install -r CAMINHO_DO_APK`. Para capturar uma falha: `adb logcat -b crash -d`. Revise e remova dados pessoais antes de compartilhar qualquer registro.

Os testes e a confirmação descritos acima são do trabalho anterior. A preparação deste repositório não compilou nem validou um novo APK na TV. Não há suíte automatizada da variante TCL incluída aqui.

Não é um patch oficial ou importável no Morphe Manager. A licença do código próprio ainda não foi definida; componentes externos mantêm suas respectivas licenças.
