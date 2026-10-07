import { describeTablePlugin } from './table-plugin-suite.ts'
import { Config } from '../src/config.ts'
import { parseMaterial, runCheck, SPEC } from '../src/model.ts'
import { buildView } from '../src/view.ts'
import { inject, name, resolvePackageFile, TOOL_NAME } from '../src/index.ts'

describeTablePlugin({
  name,
  inject,
  TOOL_NAME,
  resolvePackageFile,
  Config,
  rulesFile: 'rules/origin-rvc-check.yaml',
  parseMaterial,
  runCheck,
  buildView,
  columnNames: SPEC.columns,
  samples: {
    good: {
          "agreement": "RCEP",
          "agreementVersion": "2022 年生效文本",
          "exporter": "某某出口有限公司",
          "product": "某型电子元件",
          "fob": "400",
          "currency": "USD",
          "rvcThreshold": "",
          "rows": [
                {
                      "序号": "1",
                      "商品编号": "8541400000",
                      "品名": "某型电子元件",
                      "原产国": "日本",
                      "供应商": "某某商社",
                      "成交价格": "180",
                      "币制": "USD",
                      "非原产材料价值": "180",
                      "是否原产": "否",
                      "区域价值成分": "55.00",
                      "原产地标准": "RVC",
                      "原产地证书号": "",
                      "申报日期": "2026-03-10"
                }
          ]
    },
    unknownColumn: { rows: [{ 备注: '甲' }] },
  },
})
