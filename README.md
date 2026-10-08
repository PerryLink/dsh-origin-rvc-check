# dsh-origin-rvc-check — Regional value content check for an origin determination register

`dsh-origin-rvc-check` reads one origin determination register (原产地判定台账) — the agreement header plus one row per material — and checks that register's own arithmetic: that the agreement and product are declared, that regional value content equals (FOB − non-originating value) ÷ FOB × 100, that RVC meets the threshold you configure, that every material states its origin, that the origin criterion comes from your agreement's vocabulary, that material numbers are unique, and that no unreplaced placeholder survives in the description.

## What it answers

| You ask | What it answers |
|---|---|
| The 区域价值成分 column says `70.00`, but the row's 净价值 is `220` and the header's FOB is `400`. Is that caught? | Yes. `OR-002` recomputes the build-down formula (FOB − non-originating value) ÷ FOB × 100 from the 净价值 column and FOB, with a 0.5-point tolerance, and reports the row when the declared RVC differs. It does only the arithmetic, and it assumes the build-down method: a register filled in by the build-up method is reported although its own convention is right, so change `expression` or disable the rule. If the RVC, the 净价值 or the FOB cannot be read as a number, the rule reports itself in `skipped` instead of passing silently. |
| No threshold is set anywhere, and every row passed. Did it check the RVC at all? | No. `OR-003` ships with `threshold: 0`, which means unconfigured, so the rule reports itself in `skipped` rather than passing silently. Set `threshold` to your agreement's figure (for example `40`) and it reports each row whose RVC falls below it. A finding means only “below the threshold you set” — not that the goods are not originating, because origin can also be earned through wholly-obtained or tariff-classification-change criteria; RVC is only one path. |
| One material row leaves 原产国 blank. | `OR-004` reports every row whose 原产国 (origin) column is present but empty. It checks only that the cell is filled, not whether the declared origin is true or whether it affects origin status; when the material carries no origin column at all, the rule reports that it does not apply instead of passing silently. |
| The 原产地标准 column holds a value that is not in my list. | `OR-005` compares each value with the pack's `values` list. That list ships empty — criterion names and abbreviations differ per agreement, so the plugin hard-codes none — and the rule then reports itself in `skipped`; fill `values` with your agreement's criteria (完全获得, CTC, RVC, 特定加工工序 …) and any value not on it is reported. It checks only that the value is on the list, not that the goods satisfy that criterion. |
| The same 料件序号 appears on two rows. | `OR-006` reports a repeated 料件序号 (itemNo), comparing the values with whitespace ignored. A duplicate double-counts the non-originating material value and therefore corrupts the RVC — this is the kind of defect that leads straight to a wrong conclusion. It reports the repetition; which of the two rows is wrong is not something it decides. |
| The 品名 column still reads `【待填】` for one material. | `OR-007` reports a row whose 品名 (description) contains any of the pack's `terms` — 【, 】, `{{`, `}}`, XXX, xxx, 待填, 待补充, TBD, todo, 示例. A register copied from a template looks as if the materials had been counted, and the RVC then rests on a list of materials that does not exist. Only the listed terms are looked for, so a placeholder nobody listed passes; `terms` follows your own template. |

## Standards it follows

This rule pack cites no public standard: the verification pass obtained no verbatim text from any free trade agreement's rules of origin, so every rule's `basis` says so, each is `derived-from-principle` and none rises above `warn` or `info`. What the checks rest on instead is the register's own arithmetic, plus the RVC threshold and the criterion vocabulary you configure for the agreement that applies.

| Document | Number | Cited by rules |
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

| Surface | Status |
|---|---|
| Harness | Peer range `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verified to accept both `0.2.0-rc.2` and `0.2.1-alpha.1`. `engines.dsh` is deliberately not declared: it has no reader and cannot reject a host |
| Node | `^22.19.0 || >=24.0.0` |
| Platforms | All (plain ESM; no native code, no network, no model call) |
| Tool mode | Works in `native`, `ptc` and `both`; for a full bill of materials use `ptc` |

## What it does

Registers the `origin_rvc_check` tool. It reads one origin register — the agreement header plus one row per
material — applies a versioned rule pack, and returns a report.

| Rule | Check | Severity | Basis kind |
|---|---|---|---|
| `OR-001` | the agreement and product are declared | warn | principle |
| `OR-002` | RVC follows the deduction formula | warn | principle |
| `OR-003` | RVC meets your configured threshold (off by default) | info | local |
| `OR-004` | every material states its origin | warn | principle |
| `OR-005` | the criterion comes from your vocabulary (off by default) | info | local |
| `OR-006` | material numbers are unique | warn | principle |
| `OR-007` | the description holds no unreplaced placeholder | warn | principle |

## Install

```sh
dsh plugin --profile <name> add dsh-origin-rvc-check
dsh --profile <name> --dump-config | grep 'dsh-origin-rvc-check'
```

## Configuration

| Key | Type | Default | Description |
|---|---|---|---|
| `rulesFile` | string | `rules/origin-rvc-check.yaml` | Rule-pack path, relative to the package root |
| `disabledRules` | string[] | `[]` | Rule ids to stop running; each appears in `skipped` |
| `onlyRules` | string[] | `[]` | Run only these rule ids; empty runs every rule |
| `skipNotes` | string | `""` | Note appended to every `skipped` reason |
| `timeoutMs` | number | `120000` | Cooperative tool timeout budget |

Rule-level parameters worth knowing:

- `OR-002` `expression` / `tolerance` — the RVC formula, `percent` over `[netValue, fob]` with a 0.5-point
  tolerance. Replace it with the build-up form if your agreement uses that method.
- `OR-003` `threshold` — your agreement's RVC threshold, e.g. `40`. `0` means the rule does not run.
- `OR-005` `values` — your agreement's criteria, e.g. `[完全获得, CTC, RVC, 特定加工工序]`. Empty means no check.
- `OR-007` `terms` — the placeholders to look for.

## Material format

The tool accepts JSON or YAML:

```yaml
agreement: RCEP
agreementVersion: 2022 年生效文本
exporter: 某某出口有限公司
product: 某型电子元件
fob: '400'
currency: USD
rows:
  - { 序号: '1', 商品编号: '8541400000', 品名: 某型电子元件, 原产国: 日本,
      非原产材料价值: '180', 净价值: '220', 区域价值成分: '55.00', 原产地标准: RVC }
```

Column names are matched case-insensitively and ignoring spaces, underscores and hyphens; the register's own
column names are kept, so a finding names the column it read. A figure stated once in the header — FOB, for
instance — is found by the arithmetic checks, so it need not be repeated on every row.

## Rule sources

Rule data lives in `rules/origin-rvc-check.yaml`. Because origin rules are treaty text that the verification
pass could not obtain, the pack's `basis` entries say so explicitly instead of citing one. The load-time guard
still requires a document, clause, excerpt and source per rule, and still forbids a principle-derived or
locally configured check from being `error`.

## Troubleshooting

- **`OR-002` fires on every row.** The register was computed with the build-up method. Change `expression`, or
  disable the rule — do not widen the tolerance to hide a definition mismatch.
- **`OR-002` reports itself as skipped.** Either the net-value column is empty (the build-up method leaves it
  blank) or FOB is missing. The check will not guess which convention applies.
- **`OR-003` reports itself as skipped.** No threshold is set. Thresholds vary by agreement and tariff line, so
  the plugin hard-codes none.
- **`OR-003` fires although I believe the goods qualify.** RVC is only one path to origin. Wholly-obtained or
  tariff-classification-change criteria may still be met — confirm against the applicable agreement before
  concluding anything.
- **`OR-006` fires twice on one material.** Duplicate numbering double-counts the non-originating value and
  therefore corrupts the RVC. Correct the number.
- **The plugin installs but the tool never appears.** Check that `main` resolves to `lib/index.mjs` and
  that `pnpm run build` produced it; a wrong `main` makes the loader skip the entry silently.
- **`dsh plugin add` refuses the package as incompatible.** The peer range covers `0.1.x` and `0.2.x`; if
  your runtime sits outside it, grant an explicit exemption:
  `dsh plugin --profile <name> allow-version dsh-origin-rvc-check@0.1.0 --dsh-version <runtime> --accept-risk`
- **`check` reports `manifest-peers` as failed.** The static checker compares against a hard-coded peer
  range that predates the 0.2 line. The runtime enforces peer compatibility at install time, so the
  declared range is the correct one; this is a known upstream issue in `dsh-plugin-dev`.

## Development

```sh
pnpm install
pnpm run typecheck   # tsc --noEmit
pnpm test            # vitest, the shared table-plugin suite plus paired fixtures
pnpm run build       # tsdown -> lib/index.mjs + lib/index.d.mts
node ../scripts/sync-shared.mjs dsh-origin-rvc-check   # refresh src/shared from ../_shared
```

The plugin is **data-only**: `src/model.ts` declares the table shape, the shared kit supplies the reader and
the check engine, and the rule pack declares every check.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-origin-rvc-check contributors.
