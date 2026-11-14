---
title: "Stripe Terminal 小费处理指南：On-Reader、On-Receipt 与 PaymentIntent 捕获"
date: 2026-11-14
description: "梳理 Stripe Terminal 收取小费的不同路径，解释美国符合条件商户的 on-receipt over-capture、Tap to Pay 限制、PaymentIntent 记录与退款对账。"
slug: "stripe-terminal-tipping-on-reader-on-receipt-paymentintent-guide"
tags: ["Stripe Terminal", "Tipping", "PaymentIntent", "线下收款", "对账"]
keywords: ["Stripe Terminal 小费", "Stripe Terminal tipping", "on-receipt tipping", "PaymentIntent over-capture", "Stripe Tap to Pay 小费"]
---

# Stripe Terminal 小费处理指南：On-Reader、On-Receipt 与 PaymentIntent 捕获

餐饮、出行和个人服务等线下业务，常常需要在结账时让客户选择小费。Stripe Terminal 的小费体验可能由读卡器、商家应用或授权后的收据流程完成。不同方式对应不同的 PaymentIntent 金额和授权时点；不能只在销售系统里单独加一条 gratuity 数字，而不确认 Stripe 最终捕获了多少资金。

Stripe 官方支持文档说明，在美国，符合条件 MCC 的商户可以在确认 PaymentIntent 后通过 over-capture 收取 on-receipt tip：先授权基础消费金额，再按允许范围捕获更高金额。Stripe 列出部分符合类别的商户，并指出 Connect 平台应检查 connected account 的 MCC 是否与真实业务匹配。[Terminal on-receipt tipping 支持说明](https://support.stripe.com/questions/terminal-support-for-on-receipt-tipping)。

小费产品设计前，先明确业务所在国家、MCC、设备类型和支付方式。美国 on-receipt over-capture 的支持条件不能自动推广到其他国家；Terminal Card Reader 和 Tap to Pay 的功能也不完全一样。

## 三种小费收集体验

**On-reader tipping**：客户在支持的 Terminal 读卡器屏幕上选择小费金额，然后完成付款。小费作为本次付款金额的一部分展示给客户，商家应用可根据读卡器和 Terminal SDK/Server-driven 流程设置可选比例或固定金额。实际支持选项因设备和集成方式而异，应在目标型号上验证。

**App 侧付款前选择**：商家应用在创建或确认 PaymentIntent 前显示小费选择器，将基础金额和小费合并成最终收款金额，再发起 Terminal 支付。该方式可以在手机或平板上自定义界面，但金额计算、页面展示和后端订单明细必须一致，避免客户确认的金额和读卡器提示不同。

**On-receipt tipping**：某些符合条件的美国商户允许客户在刷卡授权后、最终捕获前写下小费，再由商户捕获超过原授权的金额。此方式具有 MCC、地区和品牌条件，不能当作所有 Terminal 付款都可使用的通用后捕获能力。Stripe 支持文档指出，符合资格的部分 MCC 包括出租车与豪华轿车、餐饮场所、酒类饮品场所、快餐店、美容理发店和健康美容水疗。

Tap to Pay 也有不同限制。Stripe Support 当前说明，Tap to Pay 不支持 on-reader tipping；商户可以在付款前自己实现小费选择屏，也可采用授权后的流程，但 post-auth tipping 必须在付款收集后 3 分钟内完成。若依赖小费且无法稳定满足时间窗口，付款前显示小费选择通常更容易保证体验。[Tap to Pay 与 Terminal 小费说明](https://support.stripe.com/questions/tap-to-pay-on-iphone-or-android-and-stripe-terminal)。

## PaymentIntent 金额模型

建议订单中分别保存商品/服务金额、税费、折扣、基础授权金额、小费和最终捕获金额。客户在授权前选择小费时，PaymentIntent 的金额可以直接反映最终预期付款。若采用 on-receipt tipping，初始授权和最终 capture 可能不同，应通过 PaymentIntent 的金额、可捕获金额与实际 captured amount 跟踪状态。

在支持 over-capture 的场景，应用不能自行假设任意金额都可以高于授权金额。确认当前 MCC、支付方式、账户和 Stripe Terminal 集成符合相关规则，再根据 API/SDK 当前参数执行。若超出允许的授权差额、超过时间限制或使用了不支持的卡品牌/地区，付款捕获可能失败。不要把通用 PaymentIntent capture 能力误解为银行卡网络和 Terminal 产品对所有交易都允许追加任意小费。

订单界面应清楚展示“商品金额 + 小费 + 税额 = 本次总金额”。如果当地税务或会计规则要求小费单独分类，应在交易明细、收据和会计导出中保留 gratuity 字段。不要只将小费并入商品单价，之后再依靠人工估算小费比例。

## 授权、捕获与交易状态

Terminal 收款流程中，客户刷卡后 PaymentIntent 可能处于需要 capture 的阶段，也可能根据集成设置在确认后自动 capture。授权阶段表示资金已获准或暂时保留，不代表最终金额已经结算。捕获后，客户账单会反映最终捕获金额；on-receipt tip 的 over-capture 流程正是利用授权与最终捕获之间的金额控制。

应用应监听和同步 PaymentIntent 状态，检查 `requires_capture`、`succeeded` 或失败状态，并在用户提交收据小费后安全更新捕获金额。读卡器动作成功事件、PaymentIntent 成功和订单完成应是可关联但不同的状态；如果读卡器显示完成，而服务端 PaymentIntent 尚未成功，后台不应立即将交易记为收款完成。

使用 Server-driven Terminal 时，跟踪 Reader action 和 PaymentIntent 当前状态。读卡器执行 capture 或其他动作失败时，记录 failure_code 与 failure_message，提供可恢复流程。不要在网络超时后盲目创建第二个 PaymentIntent，否则客户可能被重复授权或扣款。

## 退款和小费分账

退款时应明确退多少：商品部分、商品全额、小费全额或两者都退。Stripe Refund 操作通常针对付款金额，应用需维护原订单行和 gratuity 的拆分，确保收银员不会误退商品但保留不应保留的小费，或对同一交易重复退款。退款创建后，以 Refund 当前状态和 Stripe 事件更新财务记录，不要在按钮点击时就宣布退款到账。

如果商家通过 Connect 或内部工资分配流程将小费发给员工，Stripe PaymentIntent 的收款不等于小费已经转到员工。要根据平台资金流、商户责任、工资规则和适用法规另行处理分配，并审计员工、班次、原付款和退款。发卡账单上客户看到总捕获金额，并不体现商家如何在内部拆分小费。

结账小票与数字收据应展示最终金额和小费，客服和财务应能通过 PaymentIntent ID、Charge ID、Reader ID、Terminal Location、订单 ID 和小费明细互相核对。部分退款后，调整员工小费分配或薪资时也要有可追溯记录。

## 配置 MCC 与 Connect 商户

MCC（商户类别代码）描述商户业务类别。小费支持与 MCC 有关时，平台需要确认每个 connected account 的 MCC 与商户真实业务相符。不要为了开启某一功能而把商户设置成不真实的类别；错误 MCC 可能影响支付方式支持、风险评估、交易处理和合规责任。

Connect 平台应测试平台账户和 connected account 两种上下文：哪个账户创建 PaymentIntent、哪个账户捕获、资金归属哪里、交易报告记录在哪个账户，以及谁负责退款和小费处理。对于客户支持问题，明确商户还是平台负责解释付款金额。账户上下文不一致会导致查询不到预期交易或把退款发到错误账户。

## 测试与常见故障排查

测试基础付款前选择小费、读卡器小费（若设备支持）和 on-receipt over-capture 的完整金额流程。验证 PaymentIntent 金额、Reader action、最终 Charge/captured amount、收据、小票、退款和会计导出。测试时不要只看卡终端显示，还要检查服务端 Stripe 对象。

**提交 tip 后 capture 失败：**核对账户和 MCC 资格、支付品牌、原始授权金额、允许的可捕获金额、授权时间以及当前 PaymentIntent 状态。若不支持 over-capture，改用付款前小费选择流程。

**Tap to Pay 没有读卡器小费界面：**Tap to Pay 当前不支持 on-reader tipping。可以使用应用在付款前展示的选择器，或评估 3 分钟内的 post-auth 流程是否适合运营。

**Stripe 付款金额与收银系统不同：**比较 PaymentIntent、Charge、订单基础金额、小费、税额和折扣，检查重复合并小费或用了预估金额而非实际捕获金额。

**读卡器已经完成但后台订单待支付：**查询当前 Reader action 和 PaymentIntent，检查 webhook 是否收到及服务端 worker 是否更新状态。不要仅凭客户端提示重试扣款。

**Connected account 无法收取后置小费：**核对该账户国家、MCC、支付品牌、资金账户和 Terminal 配置，并咨询 Stripe Support 确认商户是否符合当前支持条件。

## 上线检查清单

- 按地区、MCC、设备和支付方式确认可用的小费流程。
- Tap to Pay 不依赖 on-reader tipping，并满足其 post-auth 时间要求或改用付款前选择。
- 订单分别保存基础金额、小费、税费、最终授权和捕获金额。
- over-capture 只用于 Stripe 当前支持的场景和金额范围。
- Receipt、Dashboard、PaymentIntent 与收银系统最终金额一致。
- Webhook、Reader action 和 PaymentIntent 状态幂等同步。
- 退款流程能指定是否退小费，并防止累计退款超过已捕获金额。
- Connect 场景下 MCC、账户上下文、资金归属和责任方正确。
- 小费分账与员工薪酬依据业务政策和适用法律另行审计。

## 总结

Stripe Terminal 小费可以在付款前由应用或读卡器收集，也可以在符合条件的美国商户场景中于授权后通过 over-capture 收取。不同方式影响 PaymentIntent 金额、客户确认体验、终端支持和退款对账。上线时要确认国家、MCC、卡品牌和设备资格，分开记录小费与商品金额，并以最终捕获金额和 Refund 状态更新订单与账务。

Terminal 小费支持受地区、商户类别、设备与支付方式限制。请以当前 Stripe Support、Terminal 文档、账户 MCC 和测试环境的实际结果为准。
