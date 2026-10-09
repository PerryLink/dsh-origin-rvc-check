# dsh-origin-rvc-check — Verificación del contenido de valor regional de un registro de determinación de origen

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-origin-rvc-check` lee un registro de determinación de origen (原产地判定台账) —la cabecera del acuerdo más una fila por material— y comprueba la aritmética de ese mismo registro: que se declaren el acuerdo y el producto, que el contenido de valor regional sea igual a (FOB − valor de los materiales no originarios) ÷ FOB × 100, que el RVC alcance el umbral que usted configura, que cada material indique su origen, que el criterio de origen proceda del vocabulario de su acuerdo, que los números de material no se repitan y que no quede ningún marcador de plantilla sin sustituir en la descripción.

## Cómo se ve la salida

![Terminal demo of dsh-origin-rvc-check: real output over its OR-001 fixture](https://raw.githubusercontent.com/PerryLink/dsh-origin-rvc-check/main/docs/assets/dsh-origin-rvc-check-demo.png)

Salida real de este plugin sobre su propio fixture de prueba `OR-001` — no es un montaje. El paquete de reglas no inventa citas, así que cada hallazgo nombra la cláusula aplicada y advierte que su texto no se obtuvo.

## Qué responde

| Usted pregunta | Qué responde |
|---|---|
| La columna «区域价值成分» dice `70.00`, pero el «净价值» de la fila es `220` y el FOB de la cabecera es `400`. ¿Se detecta? | Sí. `OR-002` recalcula la fórmula de deducción (FOB − valor de los materiales no originarios) ÷ FOB × 100 a partir de la columna «净价值» y del FOB, con una tolerancia de 0,5 puntos, y señala la fila cuando el RVC declarado no coincide. Solo hace la aritmética y supone el método de deducción: un registro calculado por el método de acumulación se señala aunque su convención sea la correcta, así que cambie `expression` o desactive la regla. Si el RVC, el «净价值» o el FOB no se pueden leer como número, la regla se informa en `skipped` en lugar de pasar en silencio. |
| No hay ningún umbral configurado y todas las filas pasaron. ¿Se comprobó el RVC? | No. `OR-003` trae `threshold: 0`, que significa sin configurar, así que la regla aparece en `skipped` en lugar de pasar en silencio. Ponga `threshold` en el valor de su acuerdo (por ejemplo `40`) y señalará cada fila cuyo RVC quede por debajo. Un hallazgo solo significa «por debajo del umbral que usted fijó», no que las mercancías no sean originarias: el origen también puede obtenerse por criterios de totalmente obtenido o de cambio de clasificación arancelaria, y el RVC es solo uno de los caminos. |
| Una fila de material deja «原产国» en blanco. | `OR-004` señala toda fila en la que la columna «原产国» (origen) existe pero está vacía. Solo comprueba que la celda esté rellenada, no si el origen declarado es cierto ni si afecta a la condición de originario; cuando el material no trae ninguna columna de origen, la regla informa de que no se aplica en lugar de pasar en silencio. |
| La columna «原产地标准» contiene un valor que no está en mi lista. | `OR-005` compara cada valor con la lista `values` del paquete. Esa lista viene vacía —los nombres y abreviaturas de los criterios cambian con cada acuerdo y el plugin no codifica ninguno— y entonces la regla se informa en `skipped`; rellene `values` con los criterios de su acuerdo (完全获得, CTC, RVC, 特定加工工序 …) y se señalará todo valor que no figure en ella. Solo comprueba que el valor esté en la lista, no que las mercancías cumplan ese criterio. |
| El mismo «料件序号» aparece en dos filas. | `OR-006` señala un «料件序号» (itemNo) repetido, comparando los valores sin tener en cuenta los espacios. Una repetición cuenta dos veces el valor de los materiales no originarios y por tanto corrompe el RVC: es el tipo de defecto que lleva directamente a una conclusión equivocada. Informa de la repetición y no decide cuál de las dos filas está mal. |
| La columna «品名» de una fila todavía dice `【待填】`. | `OR-007` señala toda fila cuyo «品名» (descripción) contenga alguno de los `terms` del paquete: 【, 】, `{{`, `}}`, XXX, xxx, 待填, 待补充, TBD, todo, 示例. Un registro copiado de una plantilla parece haber inventariado materiales reales, y el RVC acaba calculado sobre una lista de materiales que no existe. Solo busca los términos listados, así que un marcador que nadie incluyó pasa; `terms` se ajusta a su propia plantilla. |

## Normas que sigue

Este paquete de reglas no cita ninguna norma pública: la verificación no obtuvo el texto literal de las reglas de origen de ningún acuerdo de libre comercio, de modo que el `basis` de cada regla lo dice, todas son `derived-from-principle` y ninguna supera `warn` o `info`. En lo que sí se apoyan las comprobaciones es en la aritmética del propio registro y en el umbral de RVC y el vocabulario de criterios que usted configure para el acuerdo aplicable.

| Documento | Número | Reglas que lo citan |
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

| Superficie | Estado |
|---|---|
| Harness | Rango de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificado para aceptar tanto `0.2.0-rc.2` como `0.2.1-alpha.1`. **No se declara `engines.dsh`**: no tiene lector y no puede rechazar ningún host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sin código nativo, sin red, sin llamada al modelo) |
| Modo de herramienta | Funciona en `native`, `ptc` y `both`; para un directorio completo use `ptc` |

## What it does

La tabla de reglas, los campos y el comportamiento detallado están en [README.md](README.md#what-it-does) (versión principal en inglés). El plugin sólo enumera divergencias literales frente a las cláusulas citadas e indica en `skipped` cada comprobación que no pudo ejecutarse.

## Install

```sh
dsh plugin --profile <name> add dsh-origin-rvc-check
dsh --profile <name> --dump-config | grep 'dsh-origin-rvc-check'
```

## Configuration

Todos los parámetros ajustables viven en el esquema Schemastery de `src/config.ts`, por lo que se cambian desde `cordis.yml` sin tocar el código; los umbrales por regla están en el paquete de reglas bajo `rules/`.

| Clave | Tipo | Predeterminado | Descripción |
|---|---|---|---|
| `rulesFile` | string | `rules/origin-rvc-check.yaml` | Ruta del paquete de reglas, relativa a la raíz del paquete |
| `disabledRules` | string[] | `[]` | Ids de reglas que se dejan de ejecutar; cada una aparece en `skipped` |
| `onlyRules` | string[] | `[]` | Ejecutar solo estas reglas; vacío ejecuta todas |
| `skipNotes` | string | `""` | Nota añadida a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Presupuesto de tiempo de espera cooperativo de la herramienta |

## Material format

Acepta JSON o YAML. El ejemplo completo de campos está en [README.md](README.md#material-format) (versión principal en inglés). Los campos son opcionales en la capa de lectura y los valida el motor, de modo que una exportación parcial produce hallazgos sobre lo que falta en lugar de un fallo.

## Rule sources

Los datos de las reglas están separados del código: cada regla lleva documento, número, cláusula en la numeración propia de la fuente, extracto literal y URL de origen. El cargador impone que el extracto sea una cita real de al menos ocho caracteres y que una comprobación basada sólo en un principio general (`kind: derived-from-principle`, tope `warn`) o en una política local (`kind: institutional-configuration`, tope `info`) nunca se declare `error`.

Los límites verificados y las conclusiones deliberadamente **no** afirmadas están en [README.md](README.md#rule-sources) (versión principal en inglés) y en `rules/evidence/`.

## Troubleshooting

- **El plugin se instala pero la herramienta no aparece**: compruebe que `main` resuelve a `lib/index.mjs` y que `pnpm run build` lo generó.
- **`dsh plugin add` rechaza el paquete**: la faixa de peers cubre `0.1.x` y `0.2.x`; fuera de ella, conceda una exención explícita con `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Una regla no se ejecutó**: lea el arreglo `skipped`.
- **`check` informa `manifest-peers` como fallo**: es un problema conocido de `dsh-plugin-dev`; el runtime aplica la compatibilidad al instalar.
- **Los horarios parecen desplazados**: toda la aritmética es de hora local sobre las cadenas entregadas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-origin-rvc-check
```

El último comando copia el kit compartido de `../_shared` a `src/shared/`; vuelva a ejecutarlo tras cada cambio compartido.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-origin-rvc-check contributors.
