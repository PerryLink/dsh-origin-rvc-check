# dsh-origin-rvc-check — उद्गम-निर्धारण रजिस्टर के क्षेत्रीय मूल्य-अंश की जाँच

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-origin-rvc-check` एक उद्गम-निर्धारण रजिस्टर (原产地判定台账) पढ़ता है — समझौते का हेडर और प्रत्येक सामग्री की एक पंक्ति — और उसी रजिस्टर के अपने अंकगणित की जाँच करता है: कि समझौता और उत्पाद घोषित हैं, कि क्षेत्रीय मूल्य-अंश (FOB − गैर-उद्गम सामग्री मूल्य) ÷ FOB × 100 के बराबर है, कि RVC आपकी निर्धारित सीमा तक पहुँचता है, कि प्रत्येक सामग्री अपना उद्गम बताती है, कि उद्गम मानदंड आपके समझौते की शब्दावली से आता है, कि सामग्री क्रमांक दोहराए नहीं गए हैं, और कि विवरण में कोई अप्रतिस्थापित प्लेसहोल्डर शेष नहीं है।

## आउटपुट कैसा दिखता है

![Terminal demo of dsh-origin-rvc-check: real output over its OR-001 fixture](https://raw.githubusercontent.com/PerryLink/dsh-origin-rvc-check/main/docs/assets/dsh-origin-rvc-check-demo.png)

इस प्लगइन का अपने ही `OR-001` टेस्ट फ़िक्स्चर पर वास्तविक आउटपुट — कोई नकली चित्र नहीं। नियम-पैक उद्धरण नहीं गढ़ता, इसलिए हर निष्कर्ष लागू किए गए खंड का नाम और यह भी बताता है कि उसका मूल पाठ इस बार प्राप्त नहीं हुआ।

## यह किन सवालों का जवाब देता है

| आपका सवाल | इसका जवाब |
|---|---|
| «区域价值成分» कॉलम में `70.00` लिखा है, पर उस पंक्ति का «净价值» `220` है और हेडर का FOB `400` — क्या यह पकड़ में आता है? | हाँ। `OR-002` «净价值» कॉलम और FOB से कटौती-सूत्र (FOB − गैर-उद्गम सामग्री मूल्य) ÷ FOB × 100 दोबारा जोड़ता है, 0.5 अंक की सहनशीलता के साथ, और घोषित RVC मेल न खाने पर वह पंक्ति दर्ज करता है। यह केवल अंकगणित करता है और कटौती पद्धति मान लेता है: जोड़ाई पद्धति से भरा रजिस्टर भी दर्ज होगा, चाहे उसकी अपनी परिपाटी सही हो — इसलिए `expression` बदलें या नियम बंद करें। RVC, «净价值» या FOB में से कोई संख्या के रूप में न पढ़ा जाए तो यह नियम चुपचाप पास होने के बजाय `skipped` में बताता है। |
| कहीं कोई सीमा तय नहीं है और सारी पंक्तियाँ पास हो गईं। क्या RVC की जाँच हुई ही? | नहीं। `OR-003` में `threshold: 0` है, यानी अनिर्धारित, इसलिए यह नियम चुपचाप पास होने के बजाय `skipped` में आता है। `threshold` को अपने समझौते का मान दें (जैसे `40`) तो उससे नीचे रहने वाली हर पंक्ति दर्ज होगी। कोई प्रविष्टि केवल यह बताती है कि मान «आपकी तय सीमा से नीचे» है, यह नहीं कि माल उद्गम-योग्य नहीं है — उद्गम पूर्णतः-प्राप्त या सीमा-वर्गीकरण-परिवर्तन मानदंडों से भी मिल सकता है, और RVC उनमें से केवल एक रास्ता है। |
| एक सामग्री पंक्ति में «原产国» खाली छोड़ दिया गया है। | `OR-004` हर उस पंक्ति को दर्ज करता है जिसमें «原产国» (उद्गम) कॉलम मौजूद है पर खाली है। यह केवल देखता है कि कोष्ठ भरा है; घोषित उद्गम सच है या नहीं, या उससे उद्गम-स्थिति प्रभावित होती है या नहीं, यह नहीं आँकता; जब रजिस्टर में उद्गम का कोई कॉलम ही न हो, तो यह नियम चुपचाप पास होने के बजाय बताता है कि वह लागू नहीं होता। |
| «原产地标准» कॉलम में ऐसा मान है जो मेरी सूची में नहीं है। | `OR-005` हर मान की तुलना पैक की `values` सूची से करता है। वह सूची खाली आती है — मानदंडों के नाम और संक्षेप हर समझौते में बदलते हैं और यह प्लगइन कोई भी नहीं लिखता — और तब यह नियम `skipped` में बताता है; `values` में अपने समझौते के मानदंड भरें (完全获得, CTC, RVC, 特定加工工序 …) तो सूची से बाहर का हर मान दर्ज होगा। यह केवल देखता है कि मान सूची में है, यह नहीं कि माल उस मानदंड को पूरा करता है। |
| एक ही «料件序号» दो पंक्तियों में आया है। | `OR-006` दोहराया गया «料件序号» (itemNo) दर्ज करता है और तुलना करते समय खाली स्थान छोड़ देता है। दोहराव से गैर-उद्गम सामग्री मूल्य दो बार जुड़ता है और इसलिए RVC गलत हो जाता है — यह उस तरह की खोट है जो सीधे गलत निष्कर्ष तक ले जाती है। यह दोहराव दर्ज करता है; दोनों में से कौन-सी पंक्ति गलत है, यह नहीं तय करता। |
| एक पंक्ति के «品名» कॉलम में अब भी `【待填】` लिखा है। | `OR-007` हर उस पंक्ति को दर्ज करता है जिसके «品名» (विवरण) में पैक के `terms` में से कोई प्लेसहोल्डर है: 【, 】, `{{`, `}}`, XXX, xxx, 待填, 待补充, TBD, todo, 示例. टेम्पलेट से उतारा रजिस्टर ऐसा लगता है मानो असली सामग्री की गिनती हो चुकी हो, और RVC ऐसी सामग्री-सूची पर बन जाता है जो है ही नहीं। यह केवल सूचीबद्ध शब्द खोजता है, इसलिए जो प्लेसहोल्डर किसी ने नहीं जोड़ा वह छूट जाता है; `terms` अपने टेम्पलेट के अनुसार बदला जा सकता है। |

## यह किन मानकों पर आधारित है

यह नियम-पैक किसी सार्वजनिक मानक का उद्धरण नहीं देता: सत्यापन को किसी भी मुक्त व्यापार समझौते के उद्गम-नियमों का शब्दशः पाठ नहीं मिला, इसलिए हर नियम का `basis` यही बताता है, सभी `derived-from-principle` हैं और कोई भी `warn` या `info` से ऊपर नहीं जाता। जाँचें जिन पर टिकती हैं वे हैं रजिस्टर का अपना अंकगणित, और लागू समझौते के लिए आपके द्वारा निर्धारित RVC सीमा तथा मानदंड-शब्दावली।

| दस्तावेज़ | संख्यांक | इन्हें उद्धृत करने वाले नियम |
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

| सतह | स्थिति |
|---|---|
| Harness | peer रेंज `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — `0.2.0-rc.2` और `0.2.1-alpha.1` दोनों को स्वीकार करने के लिए सत्यापित। **`engines.dsh` जानबूझकर घोषित नहीं**: इसका कोई पाठक नहीं और यह किसी होस्ट को अस्वीकार नहीं कर सकता |
| Node | `^22.19.0 || >=24.0.0` |
| प्लेटफ़ॉर्म | सभी (शुद्ध ESM; कोई नेटिव कोड नहीं, कोई नेटवर्क नहीं, कोई मॉडल कॉल नहीं) |
| टूल मोड | `native`, `ptc` और `both` में काम करता है; पूरे फ़ोल्डर के लिए `ptc` चुनें |

## What it does

नियम-सूची, फ़ील्ड और विस्तृत व्यवहार [README.md](README.md#what-it-does) (अंग्रेज़ी मुख्य संस्करण) में हैं। यह प्लगइन केवल उद्धृत धाराओं के सामने शाब्दिक अंतर सूचीबद्ध करता है और हर न चल पाई जाँच को `skipped` में बताता है।

## Install

```sh
dsh plugin --profile <name> add dsh-origin-rvc-check
dsh --profile <name> --dump-config | grep 'dsh-origin-rvc-check'
```

## Configuration

सभी समायोज्य पैरामीटर `src/config.ts` की Schemastery स्कीमा में हैं, इसलिए कोड बदले बिना `cordis.yml` से बदले जा सकते हैं; प्रति-नियम सीमाएँ `rules/` के नियम-पैक में हैं।

| कुंजी | प्रकार | डिफ़ॉल्ट | विवरण |
|---|---|---|---|
| `rulesFile` | string | `rules/origin-rvc-check.yaml` | नियम-पैक का पथ, पैकेज रूट के सापेक्ष |
| `disabledRules` | string[] | `[]` | बंद करने वाले नियम id; प्रत्येक `skipped` में दिखता है |
| `onlyRules` | string[] | `[]` | केवल ये नियम चलाएँ; खाली होने पर सभी नियम चलते हैं |
| `skipNotes` | string | `""` | हर `skipped` कारण के आगे जोड़ी जाने वाली टिप्पणी |
| `timeoutMs` | number | `120000` | उपकरण का सहकारी समय-सीमा बजट |

## Material format

JSON या YAML स्वीकार्य है। पूरा फ़ील्ड उदाहरण [README.md](README.md#material-format) (अंग्रेज़ी मुख्य संस्करण) में है। पढ़ने की परत में फ़ील्ड वैकल्पिक हैं और जाँच इंजन उन्हें सत्यापित करता है, इसलिए आंशिक निर्यात पर क्रैश के बजाय "अनुपस्थित" श्रेणी के निष्कर्ष मिलते हैं।

## Rule sources

नियम-डेटा कोड से अलग है: प्रत्येक नियम में दस्तावेज़, संख्या, स्रोत की अपनी क्रमांकन-प्रणाली के अनुसार धारा, शब्दशः उद्धरण और स्रोत URL होता है। लोडर लागू करता है कि उद्धरण कम से कम आठ अक्षरों का वास्तविक उद्धरण हो, और जिस जाँच का आधार केवल सामान्य सिद्धांत (`kind: derived-from-principle`, अधिकतम `warn`) या स्थानीय नीति (`kind: institutional-configuration`, अधिकतम `info`) हो, उसे कभी `error` घोषित न किया जाए।

सत्यापित सीमाएँ और जान-बूझकर **न** कहे गए निष्कर्ष [README.md](README.md#rule-sources) (अंग्रेज़ी मुख्य संस्करण) और `rules/evidence/` में हैं।

## Troubleshooting

- **प्लगइन इंस्टॉल हो गया पर टूल दिखता नहीं**: जाँचें कि `main` `lib/index.mjs` पर जाता है और `pnpm run build` ने उसे बनाया है।
- **`dsh plugin add` असंगत बताकर मना करता है**: peer range `0.1.x` और `0.2.x` दोनों को कवर करती है; बाहर होने पर स्पष्ट छूट दें: `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`।
- **कोई नियम नहीं चला**: `skipped` सरणी देखें।
- **`check` में `manifest-peers` विफल दिखता है**: यह `dsh-plugin-dev` की ज्ञात अपस्ट्रीम समस्या है; रनटाइम इंस्टॉल के समय अनुकूलता लागू करता है।
- **समय खिसका हुआ लगता है**: सारी गणना दिए गए स्ट्रिंग पर वॉल-क्लॉक है।

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-origin-rvc-check
```

अंतिम कमांड `../_shared` का साझा किट `src/shared/` में कॉपी करता है; हर साझा बदलाव के बाद इसे दोबारा चलाएँ।

## License

[Apache License 2.0](LICENSE) © 2026 dsh-origin-rvc-check contributors.
