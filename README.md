# YouTube TV — patches locais para TCL e UnionTV

Repositório com duas variantes específicas de patch para YouTube em TVs Android. Cada variante possui seus próprios fontes, requisitos e instruções. Não é um patch genérico nem um projeto oficial do YouTube, Google, Morphe ou Cobalt.

| Variante | Base e arquitetura | Aparelho de referência | Estado |
| --- | --- | --- | --- |
| [TCL](tcl/README.md) | 7.27.302, ARMv7 | TCL 50P7K, Android TV 12 / API 31 | v3: funcionamento relatado pelo usuário; cobertura detalhada de anúncios e integrações não confirmada |
| [UnionTV](uniontv/README.md) | 5.30.340, ARMv7 | UnionTV, Android 9 / API 28 | r4: testes locais passaram; validação na TV e eficácia contra anúncios pendentes |

## Downloads

Os APKs estão disponíveis em [Releases do projeto](https://github.com/hvenanc/YouTube-TV-Patch/releases). Confira a variante e a compatibilidade descritas na release antes de instalar.

- **TCL:** `YouTube-TV-7.27.302.apk` — funcionamento relatado na TCL 50P7K com Android TV 12.
- **UnionTV:** `YouTube-TV-UnionTV-5.30.340-r4.apk` — experimental, com validação na TV pendente.

## Escolher e compilar

- Para a TCL, siga [tcl/README.md](tcl/README.md). A variante injeta JavaScript por uma chamada JNI existente no Cobalt.
- Para a UnionTV, siga [uniontv/docs/BUILD.md](uniontv/docs/BUILD.md). A variante modifica dois scripts embutidos na biblioteca Cobalt e preserva os limites de cada bloco.

Execute os comandos dentro do diretório da variante escolhida. O `package.json` e o lockfile em `uniontv/` são exclusivos dessa variante. Os scripts não devem ser intercambiados entre as bases.

```text
tcl/
  README.md          Compatibilidade, compilação, limites e validação
  src/               JavaScript e scripts Python da v3
uniontv/
  README.md          Visão geral da r4
  src/               Hooks, geração, patch e verificação
  docs/              Compilação, arquitetura, testes, histórico e referências
  package.json
  package-lock.json
```

## Escopo e limites

São tentativas locais de filtrar dados de anúncios e, na TCL, acionar botões de pular disponíveis. Alterações no servidor e anúncios não interceptados podem escapar. Login Google, Cast e integrações dependentes da assinatura original podem falhar. Não inclui SponsorBlock nem garante ausência de anúncios em vídeos ou lives.

As revisões UnionTV r1–r3 foram invalidadas por um erro no tratamento dos blocos de JavaScript; consulte o [histórico](uniontv/docs/CHANGELOG.md). O relato da variante TCL não valida a UnionTV r4.

## Conteúdo da publicação

Inclui fontes e documentação. Forneça localmente as bases compatíveis e as ferramentas indicadas nos guias. APKs, APKMs, bibliotecas, JARs, payloads derivados do Cobalt, logs, chaves e dependências instaladas não estão incluídos. O `.gitignore` exclui essas entradas e saídas nas duas variantes.

Ao relatar problemas, informe variante, revisão, base, arquitetura, Android/API e resultado observado. Remova dados pessoais dos registros antes de compartilhá-los.

## Licença e referências

A licença do código próprio ainda não foi definida; não há arquivo `LICENSE` neste pacote. Componentes externos mantêm suas respectivas licenças. Consulte as [referências UnionTV](uniontv/docs/REFERENCES.md) e as ferramentas vinculadas no [guia TCL](tcl/README.md).
