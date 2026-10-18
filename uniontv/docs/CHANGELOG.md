# Histórico

## r4 — 2026-10-18

- Preserva os limites dos quatro arrays de JavaScript embutidos no Cobalt.
- Mantém os dois primeiros arrays sem alterações e adiciona hooks nos blocos de streams/fetch, separadamente.
- Valida cada unidade como um programa independente antes do empacotamento.
- Testa inicialização sem DOM/timers, seguida da disponibilização simulada dessas APIs.
- Usa borda vermelha temporária para diagnóstico após uma chamada de parse com DOM disponível.
- Distingue o artefato pelo nome `YouTube TV UnionTV r4` e versão `5.30.340-r4`.
- Validação na TV e eficácia contra anúncios ainda pendentes.

## r1–r3 — invalidadas

A região nativa foi inicialmente tratada como um único script. A minificação conjunta deslocou o conteúdo entre arrays que o Cobalt carrega com comprimentos fixos.

O teste anterior executava a concatenação e não detectou esse erro. A reprodução com os limites originais mostrou `SyntaxError` nos quatro blocos da r2, enquanto os blocos originais passaram. O diagnóstico r3 reutilizava esse modelo de empacotamento.

Houve relatos de redução de anúncios e de persistência de anúncios iniciais, mas esses relatos não estabelecem que os hooks funcionaram. As revisões r1–r3 não são distribuídas neste conjunto de fontes e não devem ser usadas como referência de eficácia.

## Origem do trabalho

A base 5.30.340 e seu split ARMv7 foram extraídos da UnionTV pelo usuário. Uma variante anterior para YouTube 7.27.302 na TCL usava outro motor e outro ponto de injeção; não faz parte deste projeto.
