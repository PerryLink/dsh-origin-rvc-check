# dsh-origin-rvc-check — Verificação do conteúdo de valor regional de um registo de determinação de origem

`dsh-origin-rvc-check` lê um registo de determinação de origem (原产地判定台账) —o cabeçalho do acordo mais uma linha por material— e verifica a aritmética desse próprio registo: que o acordo e o produto sejam declarados, que o conteúdo de valor regional seja igual a (FOB − valor dos materiais não originários) ÷ FOB × 100, que o RVC atinja o limiar que configura, que cada material indique a sua origem, que o critério de origem venha do vocabulário do seu acordo, que os números de material não se repitam e que não reste nenhum marcador de modelo por substituir na descrição.

## O que ele responde

| Você pergunta | O que ele responde |
|---|---|
| A coluna «区域价值成分» diz `70.00`, mas o «净价值» da linha é `220` e o FOB do cabeçalho é `400`. Isso é detetado? | Sim. O `OR-002` recalcula a fórmula de dedução (FOB − valor dos materiais não originários) ÷ FOB × 100 a partir da coluna «净价值» e do FOB, com uma tolerância de 0,5 pontos, e assinala a linha quando o RVC declarado não coincide. Faz apenas a aritmética e assume o método de dedução: um registo calculado pelo método de acumulação é assinalado embora a sua convenção esteja correta, pelo que deve alterar `expression` ou desativar a regra. Se o RVC, o «净价值» ou o FOB não forem legíveis como número, a regra reporta-se em `skipped` em vez de passar em silêncio. |
| Não há nenhum limiar configurado e todas as linhas passaram. O RVC chegou a ser verificado? | Não. O `OR-003` traz `threshold: 0`, que significa não configurado, por isso a regra aparece em `skipped` em vez de passar em silêncio. Defina `threshold` com o valor do seu acordo (por exemplo `40`) e passará a assinalar cada linha cujo RVC fique abaixo dele. Uma ocorrência significa apenas «abaixo do limiar que definiu», não que as mercadorias não sejam originárias: a origem também pode ser obtida por critérios de totalmente obtido ou de mudança de classificação pautal, e o RVC é apenas um dos caminhos. |
| Uma linha de material deixa «原产国» em branco. | O `OR-004` assinala cada linha em que a coluna «原产国» (origem) existe mas está vazia. Verifica apenas que a célula está preenchida, não se a origem declarada é verdadeira nem se afeta o estatuto de originário; quando o material não tem qualquer coluna de origem, a regra reporta que não se aplica em vez de passar em silêncio. |
| A coluna «原产地标准» tem um valor que não está na minha lista. | O `OR-005` compara cada valor com a lista `values` do pacote. Essa lista vem vazia —os nomes e abreviaturas dos critérios mudam com cada acordo e o plugin não codifica nenhum— e a regra reporta-se então em `skipped`; preencha `values` com os critérios do seu acordo (完全获得, CTC, RVC, 特定加工工序 …) e qualquer valor fora dela passa a ser assinalado. Verifica apenas se o valor consta da lista, não se as mercadorias cumprem esse critério. |
| O mesmo «料件序号» aparece em duas linhas. | O `OR-006` assinala um «料件序号» (itemNo) repetido, comparando os valores sem considerar espaços. Uma repetição conta duas vezes o valor dos materiais não originários e, por isso, corrompe o RVC — é o tipo de defeito que conduz diretamente a uma conclusão errada. Reporta a repetição e não decide qual das duas linhas está mal. |
| A coluna «品名» de uma linha ainda diz `【待填】`. | O `OR-007` assinala qualquer linha cujo «品名» (descrição) contenha um dos `terms` do pacote: 【, 】, `{{`, `}}`, XXX, xxx, 待填, 待补充, TBD, todo, 示例. Um registo copiado de um modelo parece ter inventariado materiais reais, e o RVC acaba calculado sobre uma lista de materiais que não existe. Só procura os termos listados, pelo que um marcador que ninguém incluiu passa; `terms` ajusta-se ao seu próprio modelo. |

## Normas que segue

Este pacote de regras não cita nenhuma norma pública: a verificação não obteve o texto literal das regras de origem de nenhum acordo de comércio livre, pelo que o `basis` de cada regra o diz, todas são `derived-from-principle` e nenhuma passa de `warn` ou `info`. Aquilo em que as verificações se apoiam é na aritmética do próprio registo e no limiar de RVC e no vocabulário de critérios que configurar para o acordo aplicável.

| Documento | Número | Regras que o citam |
|---|---|---|
| 各自由贸易协定原产地规则（协定文本，本次未取得） | 现行协定版本本次未核实 | OR-001, OR-002, OR-003, OR-004, OR-005, OR-006, OR-007 |

**Boundary:** this plugin checks an **原产地判定台账** for arithmetic — that the agreement and product are
declared, that regional value content equals (FOB − non-originating value) ÷ FOB × 100, that RVC meets the
threshold you configure, that every material states its origin, that the origin criterion comes from your
agreement's vocabulary, that material numbers are unique, and that no placeholder survives. It does **not**
decide whether goods qualify as originating, whether a preferential rate applies, whether an origin declaration
is valid, or whether origin circumvention occurred.

> ### ⚠️ Origin rules are treaty text, and this pack does not pretend to quote one
>
> RVC and the other origin criteria — wholly obtained, change of tariff classification — are set by **each free
> trade agreement's rules of origin**. RCEP, ASEAN–China, China–Korea and the rest differ in their thresholds
> (40%, 30% and other tiers) and in their calculation methods. **The verification pass obtained no verbatim text
> from any agreement**, so every rule's `basis` says exactly that and stays at `warn` or `info`.
>
> Three consequences are worth knowing before trusting a finding:
>
> - **`OR-002` assumes the build-down method** — RVC = (FOB − VNM) ÷ FOB × 100. Some agreements permit the
>   **build-up** method (regional value ÷ FOB × 100), which yields a different number for the same goods. A
>   register computed that way will report a difference; change `expression` or disable the rule. The check
>   reads FOB and the net value through a header fallback, so a figure stated once for the whole set is found.
> - **`OR-003`'s threshold ships unset.** Thresholds vary by agreement *and* by tariff line, so the plugin
>   hard-codes none. A finding means "below the threshold you set", **not** "these goods are not originating" —
>   because origin can also be earned through wholly-obtained or tariff-classification-change criteria.
>   **RVC is only one path.** That distinction matters, and the rule's note states it.
> - **`OR-005`'s criterion vocabulary ships empty**; criterion names and abbreviations differ per agreement.

## Compatibility

| Superfície | Estado |
|---|---|
| Harness | Faixa de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificada para aceitar tanto `0.2.0-rc.2` quanto `0.2.1-alpha.1`. **`engines.dsh` não é declarado**: não tem leitor e não pode recusar nenhum host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sem código nativo, sem rede, sem chamada ao modelo) |
| Modo de ferramenta | Funciona em `native`, `ptc` e `both`; para um diretório inteiro use `ptc` |

## What it does

A tabela de regras, os campos e o comportamento detalhado estão em [README.md](README.md#what-it-does) (versão principal em inglês). O plugin apenas lista divergências literais frente às cláusulas citadas e indica em `skipped` cada verificação que não pôde ser executada.

## Install

```sh
dsh plugin --profile <name> add dsh-origin-rvc-check
dsh --profile <name> --dump-config | grep 'dsh-origin-rvc-check'
```

## Configuration

Todos os parâmetros ajustáveis ficam no esquema Schemastery de `src/config.ts`, portanto mudam pelo `cordis.yml` sem editar código; os limites por regra ficam no pacote de regras sob `rules/`.

| Chave | Tipo | Padrão | Descrição |
|---|---|---|---|
| `rulesFile` | string | `rules/origin-rvc-check.yaml` | Caminho do pacote de regras, relativo à raiz do pacote |
| `disabledRules` | string[] | `[]` | Ids de regras a desativar; cada uma aparece em `skipped` |
| `onlyRules` | string[] | `[]` | Executar apenas estas regras; vazio executa todas |
| `skipNotes` | string | `""` | Nota acrescentada a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Orçamento de tempo limite cooperativo da ferramenta |

## Material format

Aceita JSON ou YAML. O exemplo completo de campos está em [README.md](README.md#material-format) (versão principal em inglês). Os campos são opcionais na camada de leitura e validados pelo motor, de modo que uma exportação parcial gera achados sobre o que falta em vez de falhar.

## Rule sources

Os dados das regras ficam separados do código: cada regra traz documento, número, cláusula na numeração própria da fonte, trecho literal e URL de origem. O carregador impõe que o trecho seja citação real de pelo menos oito caracteres e que uma verificação baseada apenas em princípio geral (`kind: derived-from-principle`, teto `warn`) ou em política local (`kind: institutional-configuration`, teto `info`) nunca seja declarada `error`.

Os limites verificados e as conclusões deliberadamente **não** afirmadas estão em [README.md](README.md#rule-sources) (versão principal em inglês) e em `rules/evidence/`.

## Troubleshooting

- **O plugin instala mas a ferramenta não aparece**: confirme que `main` resolve para `lib/index.mjs` e que `pnpm run build` o gerou.
- **`dsh plugin add` recusa o pacote**: a faixa de peers cobre `0.1.x` e `0.2.x`; fora dela, conceda isenção explícita com `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Uma regra não executou**: leia o arranjo `skipped`.
- **`check` informa `manifest-peers` como falha**: problema conhecido do `dsh-plugin-dev`; o runtime aplica a compatibilidade na instalação.
- **Os horários parecem deslocados**: toda a aritmética é de hora local sobre as cadeias fornecidas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-origin-rvc-check
```

O último comando copia o kit compartilhado de `../_shared` para `src/shared/`; execute-o novamente após cada alteração compartilhada.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-origin-rvc-check contributors.
