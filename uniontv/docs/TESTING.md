# Testes e diagnóstico

## Evidência disponível

| Verificação | Estado na r4 |
| --- | --- |
| Sintaxe e execução individual dos quatro blocos | Passou em Node.js |
| Inicialização simulada sem DOM/timers | Passou |
| Streams, Headers e Response text/json exercitados | Passou com auxiliares simulados |
| Filtragem aninhada, revivers e erros de JSON | Passou nos casos exercitados |
| Flag de solicitação e objeto de entrada preservado | Passou nos casos exercitados |
| Borda temporária e timer único | Passou em DOM simulado |
| Empacotamento local, integridade ZIP, manifesto e assinatura | Verificados no artefato local |
| Execução da r4 na UnionTV | Pendente |
| Bloqueio de anúncios iniciais, intermediários e em lives | Pendente |

Não interpretar o sucesso em Node.js como prova de reprodução ou de bloqueio de anúncios no aparelho.

## Executar os testes locais

Após preparar `build/libcobalt-original.so` e gerar o payload:

```bash
npm run verify -- build/libcobalt-original.so
```

O verificador executa original e r4 com os quatro limites fixos, em contextos separados. Só depois adiciona os auxiliares que representam APIs do ambiente. Ele exercita dados de teste e não faz chamadas ao YouTube ou a serviços externos.

## Validação no aparelho

Registre os seguintes resultados para a **r4**, sem extrapolar de revisões anteriores:

1. O APK instala e o nome aparece como `YouTube TV UnionTV r4`?
2. O aplicativo abre e permite buscar/reproduzir um vídeo?
3. A borda vermelha aparece brevemente ao carregar conteúdo?
4. O mesmo vídeo apresenta anúncio antes de começar?
5. Um vídeo longo apresenta interrupção por anúncio?
6. Uma live apresenta anúncio ao entrar ou durante a transmissão?
7. Áudio, controle remoto e avanço continuam funcionando?

A frequência de anúncios varia. Um teste sem anúncio não comprova bloqueio confiável. Registre horário, quantidade de tentativas, tipo de conteúdo e eventual botão/contagem do anúncio.

## Capturar o início completo

```bash
adb shell am force-stop local.youtubetv.uniontv
adb logcat -T 1 -v time > inicio-local.log
```

Com a captura rodando, abra o app e reproduza até o evento investigado. Encerre com Ctrl+C. O arquivo é local e ignorado pelo Git. Se houver fechamento:

```bash
adb logcat -b crash -d
```

Revise os dados antes de incluir um trecho em uma issue. O log pode conter informações do aparelho ou da conta.

## Ausência de marcadores

As revisões antigas usavam mensagens `UTVAds` e um elemento de texto `UTV3`. A r4 usa a borda temporária e versão de manifesto própria. Não reutilize os filtros de log antigos para concluir se a r4 executou.

Se a borda não aparecer, registre isso sem atribuir automaticamente a uma causa: podem existir limitações de execução, disponibilidade do DOM ou apresentação. Se aparecer, demonstra execução do hook e acesso ao DOM, não eficácia de todos os filtros.
