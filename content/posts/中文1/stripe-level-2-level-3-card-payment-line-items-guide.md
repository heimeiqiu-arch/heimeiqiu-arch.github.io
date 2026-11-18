---
title: "Stripe 卡交易 Level 2 与 Level 3 数据：行项目字段、金额校验和对账"
date: 2026-11-15
description: "Stripe Level 2/Level 3 支付数据指南：整理 PaymentIntent 行项目、商品编码、税额、折扣和订单参考字段，并说明算术校验与实际资格验证。"
slug: stripe-level-2-level-3-card-payment-line-items-guide
tags:
  - PaymentIntent
  - Level 2
  - Level 3
  - 卡交易数据
keywords:
  - Stripe Level 2 数据
  - Stripe Level 3 行项目
  - PaymentIntent amount_details line_items
  - Stripe 企业卡交易数据
  - Stripe 卡支付订单参考
---

# Stripe 卡交易 Level 2 与 Level 3 数据：行项目字段、金额校验和对账

企业采购、商业卡和采购卡交易有时需要随付款提交比普通卡交易更详细的订单信息，例如订单参考、税额、商品名称、数量、单价和商品代码。Stripe PaymentIntent 提供 amount_details 等字段承载部分行业数据，用于在适用的卡交易流程中传递交易细节。开发者常把这类数据称为 Level 2 或 Level 3 信息。

提交字段并不保证交易一定符合某种卡网络定价、商户资格或发卡方处理条件。卡组织、收单安排、商户类别和交易类型都会影响最终结果。本文聚焦 API 数据组织和系统核对：怎样从订单系统生成真实行项目、避免金额不一致、以及如何用实际交易确认数据有没有按预期传递。涉及费率、卡网络优惠或资格结论，应向 Stripe 或收单服务商确认，不要仅靠提交更多字段推断一定节省成本。

## Level 2/Level 3 字段的业务来源

最可靠的数据来源是支付时的订单快照，而不是开发者在后端临时拼写的描述。创建 PaymentIntent 或进行捕获流程时，整理真实商品行项目，包括产品名称、数量、单位成本、折扣、税额、商品代码、运费和订单参考。Stripe 文档列出部分字段在特定 Level 2 或 Level 3 数据场景下的要求；例如交易级订单参考、税额，以及行项目的名称、数量和单位成本等。

在电商系统中，订单通常已有内部 SKU、名称、计价单位、数量和折扣。将内部字段映射到 Stripe API 时，先确定金额用的是最小货币单位，且币种精度遵循 Stripe 对该币种的规则。不能把“元”直接按小数字符串传给要求整数最小单位的参数，也不能把订单展示文案截断后误当成实际商品价格。

| 业务数据 | 可能对应的 Stripe 信息 | 生成依据 |
| --- | --- | --- |
| 商户订单号 | order_reference | 服务端创建的唯一订单引用 |
| 商品名称 | line_items.product_name | 结账时购买的商品快照 |
| SKU 或商品分类号 | product_code、commodity_code | 商户商品目录 |
| 数量和单价 | quantity、unit_cost | 经验证的订单行项目 |
| 折扣 | 行项目折扣或交易级折扣 | 优惠计算后的实际折扣 |
| 税额 | 行项目税额或交易级税额 | 税务计算和订单快照 |
| 运费 | shipping.amount 等字段 | 订单中实际收取的配送费用 |

不要把 card network commodity code 与商户内部 SKU 混淆。SKU 用于识别自己的商品；commodity_code 是按对应字段和网络要求使用的商品分类代码。字段长度和字符限制也可能不同，必须查 API 当前参数说明，而不是把内部 50 位 SKU 不加处理直接塞进去。

## 从订单计算 PaymentIntent 数据

先在服务端建立付款订单并冻结一份结账快照：商品、数量、单价、折扣、税、运费、订单总额和币种。再根据 Stripe 字段要求生成 amount_details，确保所有传递字段来自同一份快照。若客户在付款前修改购物车或折扣，重新计算订单与付款金额后再确认；不要将旧行项目与新总额混合提交。

算术关系是首要校验点。行项目数量乘以单位成本、减去折扣、加上税和运费后，应与 PaymentIntent 金额及实际订单总额遵循你业务规定的关系。Stripe API 提供 enforce_arithmetic_validation 等相关行为；开启严格校验有助于尽早发现行项目算术错误。若选择允许计算继续而不因算术错误失败，Stripe 文档说明对卡交易可能不会向卡网络发送行项目数据，因此不能把“付款请求成功”当成“Level 3 信息已成功传递”。

金额运算使用整数最小货币单位或可靠的十进制定点库，避免二进制浮点误差。折扣要明确放在交易级还是行项目级字段；API 可能规定两种表示互斥。税也可能是按交易总额或逐商品明细传递，不能重复计算。商品数量必须大于零，单位成本和税额不能是负数，SKU 与商品名称需要在 API 限长内。

## API 约束与字段边界

PaymentIntent API 的捕获端点文档展示了 amount_details、line_items、shipping、tax 和 final_capture 等捕获参数。实际应在创建、确认或捕获哪个阶段传递数据，要按照你当前集成和 API 版本的官方指南确认。不要仅凭某个捕获端点示例推断所有字段都能在任何付款方式、任何 API 生命周期阶段修改。

当前文档对行项目数量和字段长度给出限制。例如行项目列表有最大项数，product_name、product_code、commodity_code 也各有长度约束。订单有更多商品时，需按 Stripe 文档规定选择汇总、映射或其他受支持方式，不要自行拆成多个 PaymentIntent 来绕过字段限制，因为那会变成多笔交易并影响顾客账单与退款。

使用 Checkout、Payment Links 或其他封装集成时，API 细节可能不同。先确认对应产品是否能传递需要的行业数据，再决定是否需要直接调用 PaymentIntent API。产品对象的行项目与交易提交给卡网络的行项目也不是同一个概念；确保数据位于 Stripe API 支持的字段中，而不是只写在 Product 描述或 metadata 里。

## 常见的行项目错误

**交易总额与行项目不相符：**检查数量、单价、折扣、税和运费的计算顺序，确认币种小数位和舍入规则一致。把金额拆成最小货币单位后，确保各个分项与实际扣款一致。

**重复计算折扣或税额：**交易级折扣与逐行折扣不要同时表达同一优惠；税额要确认是行项目级还是订单级，并和 Stripe Tax 计算结果保持一致。订单后台显示的税率百分比不能直接替代实际计算出的税额字段。

**使用错误商品编码：**确认 product_code 与 commodity_code 分别来自正确的内部目录字段，字符长度满足 API 约束。不要为了填字段随机生成代码，或把不同实际商品都映射成一个不透明值后假设其分类有效。

**用展示名称替代商品快照：**商品名称可能之后编辑或本地化。保存付款时的名称、单价、SKU 和折扣快照，才能在争议、退货和财务审计时复原当时交易。

**只检查 API 响应状态：**PaymentIntent 创建成功并不说明卡网络接受了全部附加数据。检查请求日志、对象字段、Stripe Dashboard 的交易记录和可用的网络数据报告；必要时询问 Stripe 支持交易数据是否按预期传递。

## 验证和监控方案

在测试环境构造几种订单：单一商品、多行商品、折扣、税额、运费、退货或部分退款场景。核对提交给 Stripe 的字段、PaymentIntent 金额和本地订单快照。再对真实适用的测试卡或测试流程检查 Dashboard 是否暴露相应信息；测试环境的结果不保证代表正式卡网络和账户资格。

正式上线后监控 amount_details 缺失率、算术验证失败率、API 参数错误、订单总额和 PaymentIntent 金额差异。对于异常订单保存 Stripe request ID、PaymentIntent ID、内部 order_id 和错误码，避免把完整卡数据记录在日志中。若业务或卡网络报告指出提交数据未被接受，按字段层级对比实际请求，而不是先改动金额或自动重试付款。

可以建立一个服务端校验函数：输入订单快照，验证所有字段的类型和长度；计算总金额并和 PaymentIntent 金额比对；拒绝重复 SKU 或无效数量；再生成 Stripe 参数。该函数应作为单元边界在每次价格、税务或优惠规则变化时复查，避免一个结账入口添加了新折扣字段，而另一个入口仍发送旧数据结构。

## 总结

Level 2/Level 3 数据的重点是提供真实、可对账的交易明细，并满足 Stripe API 对字段和算术的要求。把订单号、商品、数量、单价、折扣、税和运费从服务端订单快照生成，区分 SKU 与卡网络商品代码，严格校验字段限制和总额一致性。字段提交成功不等于卡网络资格、费率或特定处理结果已保证；上线后需要通过实际交易和 Stripe 支持渠道确认。

请参阅 Stripe 的[PaymentIntent 捕获 API](https://docs.stripe.com/api/payment_intents/capture)、[PaymentIntent 对象](https://docs.stripe.com/api/payment_intents/object)、[PaymentIntent 创建指南](https://docs.stripe.com/api/payment_intents/create)和[Webhook 文档](https://docs.stripe.com/webhooks)。
