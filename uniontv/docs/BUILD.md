# Compilação e instalação

Execute os comandos na raiz do repositório. Use uma pasta `build/` nova para cada compilação; `prepare` não deve ser aplicado duas vezes à mesma decodificação.

## Dependências e entradas

Ambiente usado: Java 21, Python 3.12, Node.js 24.18.0, npm e `unzip`.

Obtenha pelos projetos de origem:

- [Apktool 2.12.1](https://github.com/iBotPeaches/Apktool/releases/tag/v2.12.1), salvo como `tools/apktool.jar`.
- [Uber APK Signer 1.3.0](https://github.com/patrickfav/uber-apk-signer/releases/tag/v1.3.0), salvo como `tools/uber-apk-signer.jar`.

Forneça os dois APKs extraídos de uma instalação compatível de YouTube TV 5.30.340:

```text
input/base.apk
input/split_config.armeabi_v7a.apk
```

O APK base esperado tem SHA-256:

```text
570f5f4f85740f9a71056de87552d7adfbe639845fa77a745c493933090954a7
```

A biblioteca `lib/armeabi-v7a/libcobalt.so` dentro do split deve ter SHA-256:

```text
a3bc2715219e534f7d06d2d36321d9e0d51133c6ff80f97ef5f4ae16d94a7719
```

Uma diferença de hash exige nova análise, mesmo que o nome da versão seja igual. Não remova as verificações para forçar outro APK.

## 1. Preparar o JavaScript

```bash
npm ci
mkdir -p build
unzip -p input/split_config.armeabi_v7a.apk lib/armeabi-v7a/libcobalt.so > build/libcobalt-original.so
npm run generate -- build/libcobalt-original.so src/cobalt-startup-patched.js
npm run verify -- build/libcobalt-original.so
```

O gerador extrai os scripts do seu binário e preserva o tamanho de cada bloco. O arquivo `src/cobalt-startup-patched.js` é um artefato derivado, não incluído no repositório. Gere-o sempre antes de empacotar. Se qualquer verificação falhar, investigue antes de continuar.

## 2. Preparar e compilar o DEX

```bash
java -jar tools/apktool.jar d -f -p build/framework -o build/decoded input/base.apk
python3 src/patch_uniontv.py prepare build/decoded
java -jar tools/apktool.jar b -p build/framework -o build/dex-source.apk build/decoded
```

O resultado intermediário fornece o DEX alterado. Seus recursos recompilados não são usados na etapa seguinte.

## 3. Empacotar preservando os recursos originais

```bash
python3 src/patch_uniontv.py package input/base.apk input/split_config.armeabi_v7a.apk build/dex-source.apk build/unsigned.apk
```

O empacotador usa os recursos e assets originais, aplica as alterações ao manifesto binário, inclui as oito bibliotecas ARMv7 e verifica a integridade ZIP. Apenas o trecho dos scripts de `libcobalt.so` é modificado; as outras sete bibliotecas ficam intactas.

## 4. Assinar

```bash
java -jar tools/uber-apk-signer.jar --apks build/unsigned.apk --out dist
```

O signer informa o caminho e o resultado da verificação de assinatura/alinhamento. Com esses nomes de entrada, a saída usual é `dist/unsigned-aligned-debugSigned.apk`:

```bash
cp dist/unsigned-aligned-debugSigned.apk dist/YouTube-TV-UnionTV-5.30.340-r4.apk
```

O artefato local de referência usou o certificado de depuração embutido no signer. O programa pode escolher outro keystore de depuração se houver um configurado no computador. Confirme o certificado usado; para atualizar uma instalação existente, ele deve ser o mesmo. Não há chave privada neste repositório.

A compilação não promete um APK byte a byte idêntico ao artefato de referência; assinatura e ferramentas podem produzir hashes diferentes.

## 5. Instalar na TV

Com ADB já autorizado e conectado:

```bash
adb devices
adb install -r dist/YouTube-TV-UnionTV-5.30.340-r4.apk
```

O pacote gerado é `local.youtubetv.uniontv`, distinto do oficial. O Android mínimo continua API 24, como no original. Isso permite a tentativa em Android 9, mas não garante funcionamento em todo aparelho com API 24 ou superior.

Depois da instalação, execute a [validação no aparelho](TESTING.md). Não altere `minSdkVersion` para contornar um erro de instalação sem investigar as APIs efetivamente usadas.

## Se uma etapa falhar

- **Hash diferente:** confira variante, arquitetura e arquivos extraídos.
- **Patch já aplicado:** use uma decodificação nova.
- **Payload ausente:** execute `npm run generate` antes de `package`.
- **Bloco sem espaço:** não remova a verificação de tamanho; reduza o hook e repita os testes separados.
- **Falha de assinatura na atualização:** confira se o certificado coincide com o da instalação.
- **Aplicativo fecha:** obtenha `adb logcat -b crash -d` e registre a exceção completa relevante.
