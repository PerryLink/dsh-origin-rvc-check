/**
 * dsh-origin-rvc-check — table shape and material contract.
 *
 * The plugin is data-only: this file declares which columns the material may use
 * and how they map onto canonical field names; the shared kit supplies the reader
 * and the check engine, and the rule pack declares every check. Adding a check
 * that fits an existing kind is a rule-pack edit, not a code change.
 */

import { canonicaliseRow, parseTable, type TableSpec } from './shared/table.ts'
import { runTableCheck, type TableCheckOptions, type TableInput } from './shared/rows.ts'
import type { Ruleset } from './shared/rules.ts'

/** Tool id exposed to the model, and the row id in `cordis.patch.yml`. */
export const TOOL_NAME = 'origin_rvc_check'

/** The register's column aliases, declared once so both the spec and the guard see them. */
const COLUMNS = {
  itemNo: ['序号', '料件序号', '项号', 'itemNo'],
  hsCode: ['商品编号', 'HS编码', '税则号列', 'hsCode'],
  description: ['品名', '商品名称', '料件名称', 'description'],
  origin: ['原产国', '原产地', 'origin'],
  supplier: ['供应商', '供货商', 'supplier'],
  price: ['成交价格', '价格', '单价', 'price'],
  currency: ['币制', '币种', 'currency'],
  vnm: ['非原产材料价值', 'VNM', '非原产价值', 'vnm'],
  /**
   * The net value the deduction formula divides by.
   *
   * RVC under the build-down method is (FOB - VNM) / FOB; the formula check reads
   * this column. A register using the build-up method fills `rvc` directly and
   * leaves this blank, and the check then reports that it could not run rather
   * than guessing which convention applies.
   */
  netValue: ['净价值', 'FOB减非原产材料价值', '扣减后价值', 'netValue'],
  isOriginating: ['是否原产', '原产材料', 'isOriginating'],
  rvc: ['区域价值成分', 'RVC', '增值率', 'rvc'],
  criteria: ['原产地标准', '原产地判据', '标准', 'criteria'],
  certNo: ['原产地证书号', '证书编号', 'certNo'],
  declaredAt: ['申报日期', '日期', 'declaredAt'],
  note: ['备注', '说明', 'note', 'remark'],
} as const

/** How the material declares its table. */
export const SPEC: TableSpec = {
  rowKeys: ['rows', 'items', 'materials', '料件'],
  columns: COLUMNS,
  header: {
  agreement: ['agreement', '协定名称', '适用协定'],
  agreementVersion: ['agreementVersion', '协定版本', '规则版本'],
  exporter: ['exporter', '出口商', '出口方'],
  product: ['product', '产品名称', '货物名称'],
  fob: ['fob', 'FOB 价格', '离岸价'],
  currency: ['currency', '币制', '币种'],
  rvcThreshold: ['rvcThreshold', 'RVC 门槛', '区域价值成分门槛'],
  checkedAt: ['checkedAt', '核对日期'],
  },
}

/** Fields the material must carry somewhere for the reader to accept it. */
export const REQUIRE_ANY_OF = [
  '原产国',
  'origin',
  '非原产材料价值',
  'vnm',
  '区域价值成分',
  'rvc',
  '原产地标准',
  'criteria',
]

/**
 * Parse the material and attach its canonical field names.
 * @param source - JSON or YAML text.
 * @param target - description of where the material came from.
 * @returns the normalized table, with each row's aliases resolved to field names.
 */
export function parseMaterial(source: string, target: string): TableInput {
  const table = parseTable(source, target, {
    ...SPEC,
    ...(REQUIRE_ANY_OF === undefined ? {} : { requireAnyOf: REQUIRE_ANY_OF }),
  })
  for (const row of table.rows) canonicaliseRow(row, SPEC)
  return table
}

/**
 * Run the rule pack against the material.
 * @param input - normalized table.
 * @param ruleset - validated rule pack.
 * @param options - plugin identity, clock value, rule selection and overrides.
 * @returns the report.
 */
export function runCheck(input: TableInput, ruleset: Ruleset, options: TableCheckOptions) {
  return runTableCheck(input, ruleset, options)
}

export type { TableCheckOptions, TableInput }
