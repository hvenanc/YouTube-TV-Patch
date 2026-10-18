# Arquitetura do patch r4

## Carregamento dos scripts

Na base analisada, `libcobalt.so` contém quatro arrays contíguos de JavaScript. O Cobalt avalia cada array com seu próprio tamanho; não executa a região inteira como um único programa.

O offset inicial no arquivo é `0x853944`. A região tem 22.137 bytes e SHA-256:

```text
9ce14385832aabc7fd36569d89ceeef0e2dc589c8136386396fa6ba580a09300
```

| Bloco | Início relativo, bytes | Tamanho, bytes | Alteração |
| --- | ---: | ---: | --- |
| `byte_length_queuing_strategy.js` | 0 | 305 | Nenhuma |
| `count_queuing_strategy.js` | 305 | 289 | Nenhuma |
| `readable_stream.js` | 594 | 10257 | Minificação local + hook de parse |
| `fetch.js` | 10851 | 11286 | Minificação local + hook de stringify |

O gerador compartilha constantes de texto repetidas dentro de cada bloco, preservando seus valores, e minifica com Terser 5.44.0. O espaço restante é preenchido com espaços. Nenhum script pode atravessar seu limite. Os dois primeiros blocos ficam idênticos aos originais.

## Hooks

`parse.js` guarda as funções nativas de JSON e as chaves compartilhadas em `__utv4`. O reviver trata campos aninhados:

- `playerAds` → `false`;
- `adPlacements`, `adSlots`, `adBreaks` → arrays vazios.

Um reviver personalizado, quando fornecido, recebe os valores já tratados. Isso é uma alteração intencional dos dados, não uma equivalência geral ao `JSON.parse` original.

`stringify.js` reconhece objetos com `playbackContext.contentPlaybackContext`, clona o objeto pelo caminho JSON e acrescenta `isInlinePlaybackNoAd: true` quando necessário. O objeto original não é modificado nos casos testados. O replacer e a indentação são repassados à serialização final. Objetos com `toJSON` e efeitos colaterais podem ter comportamento diferente, pois a clonagem exige uma serialização adicional.

Os hooks não decodificam protobuf, não analisam áudio, não removem trechos gravados pelo criador e não garantem tratamento de anúncios integrados ao fluxo de mídia.

## Diagnóstico visual

O hook de parse tenta aplicar uma borda vermelha no `body` e removê-la após 10 segundos. A tentativa ocorre durante o uso do hook, após o carregamento dos arrays, quando o DOM já pode estar disponível. Falhas por indisponibilidade do DOM são ignoradas e a próxima chamada pode tentar novamente.

O modelo de teste não fornece DOM/timers na avaliação inicial e só adiciona essas APIs depois. A apresentação real no aparelho continua pendente.

## Manifesto, DEX e bibliotecas

O manifesto é editado no formato AXML para manter os índices dos recursos originais. O pacote passa a `local.youtubetv.uniontv`, o nome a `YouTube TV UnionTV r4` e a versão de manifesto a `5.30.340-r4`. O `versionCode` permanece `530340320` e o mínimo de API continua 24.

O APK único inclui as bibliotecas ARMv7 do split e usa extração de bibliotecas nativas. As exigências de splits no manifesto são removidas após a união.

No DEX, strings de pacote usadas em permissões e integrações internas são ajustadas. A recusa específica `PackageVerificationRslt: not allowed:` é encaminhada ao callback de falha já existente em GMS. A resposta do serviço continua sendo uma recusa; não há alteração da assinatura apresentada ou autorização de serviços. Outras mensagens de `SecurityException` são relançadas.

## Escopo dos testes

Os testes verificam os blocos separadamente e exercitam funções em Node.js com auxiliares nativos simulados. Não emulam integralmente o Cobalt nem validam a resposta do servidor do YouTube. Consulte [TESTING.md](TESTING.md).
