---
title: "Stripe Connect 资金流怎么选：Direct、Destination 与 Separate Charges"
date: 2026-11-19
slug: stripe-connect-charge-types-funds-flow-risk-guide
description: "比较 Stripe Connect Direct charges、Destination charges 和 Separate charges and transfers 的资金流、商户账单展示、退款、拒付责任与适用场景，帮助平台选对收款架构。"
keywords:
  - Stripe Connect 资金流
  - Stripe Direct charges
  - Stripe Destination charges
  - Separate charges and transfers
  - Stripe Connect 退款责任
  - Stripe Connect 拒付资金
tags:
  - Stripe
  - Stripe Connect
  - 平台支付
  - 资金流
---

Stripe Connect 平台在设计收款方式时，往往会先关注“如何把一部分钱转给卖家”。但 Connect charge type 同时决定支付在哪个 Stripe 账户创建、款项如何分配、客户账单上显示谁、Stripe 费用由谁承担，以及退款和拒付先从哪个账户余额扣款。若只根据 API 参数看起来是否方便选择模式，后续可能发现平台承担了未预期的争议成本，或无法实现一笔购物车拆给多个商家。

Stripe Connect 常见收费架构包括 Direct charges、Destination charges 和 Separate charges and transfers。它们并非简单的三种写法，而是对应不同的平台业务关系和资金责任。本文从平台与卖家关系、资金归属、退款和争议处理角度比较三种模式，并给出选型时的检查问题。实际支持能力会受账户类型、国家、功能和 Stripe 配置影响，上线前应检查 Dashboard 平台配置和当前官方文档。

## 先问谁在向客户销售

选择 charge type 前，先确认客户认为自己在向谁购买。客户是否直接与卖家交易，还是平台向客户提供一个统一服务？订单中涉及一个 connected account 还是多个？创建付款时，平台是否已经知道资金接收方？退款、拒付和 Stripe 费用由谁承担？这些业务问题会决定资金流模式。

支付对象创建在哪个账户上，通常影响 Dashboard 中支付归属和账单展示；款项归属又影响退款、争议和负余额处理。财务部门、客服和法律条款需要与工程团队使用同一套业务定义。不能只看手续费差异选择模式，而忽略平台与卖家之间的合同责任和风险承担。

一个平台可以在不同业务流程中使用多种 charge type，但每条产品线都应清楚说明其对象归属和资金流。混用模式时，内部订单需要记录 charge 所属账户、connected account、transfer 关系、application fee 和退款/争议责任，避免日后只靠订单总金额推断资金去了哪里。

## Direct charges：卖家直接向客户收款

Direct charge 在 connected account 上创建。适合客户主要与卖家交易、平台提供软件或工具、每笔交易对应一个 connected account 的场景。平台可以根据账户能力和配置收取 application fee；客户付款会显示在 connected account 的余额中，而非平台余额中。

这种方式的资金和支付对象更贴近卖家账户。Stripe 文档说明，Direct charge 的退款和拒付会减少 connected account 余额；Stripe 费用可以根据配置从 connected account 或平台账户扣除。付款通常在 connected account 所在国家结算。平台应向卖家说明交易、退款和争议如何在其账户中呈现，并确保相关能力已激活。

Direct charge 常用于提供电商店铺、账单收款或 SaaS 支付能力的平台。在 Stripe 的连接账户设置中，账户类型和 capability 影响可用方案；官方文档指出 Direct charge 需要 connected account 具备 active 的 card_payments capability，并对某些 legacy Express/Custom 账户类型给出迁移或改用方案建议。实现前必须核对当前账户类型，不应默认每种 Connect 账户都支持同样的收费方式。

在使用 Direct charge 时，平台通常不先把整笔交易接收到自己的余额再拆款。财务对账应从 connected account 交易和 application fee 角度进行。退款时要确认 connected account 余额是否足够；如果余额不足，退款可能处于 pending，具体状态与账户情况有关。

## Destination charges：平台收款后立即向一个卖家转款

Destination charge 在平台账户创建付款，并立即将全部或部分资金转至一个 connected account。适合客户认为自己在与平台交易、但实际商品或服务由一个卖家提供的市场或服务平台。平台余额通常承担 Stripe 费用、退款和争议扣款。

平台可以在转账金额中扣除 application fee，或按业务设计另外处理平台费用。款项先由平台创建 charge，再转至一个 connected account，适合一笔交易对应一个明确服务提供者的场景。例如乘客向网约车平台付款、平台立即向一名司机分配该笔收入，或客户通过统一品牌购买一个承包商的服务。

由于付款建立在平台账户上，支付详情、客户对账单和风险责任需要与平台对外品牌保持一致。若使用 on_behalf_of 将 connected account 指定为记录商户，Stripe 会根据相关设置影响结算国家、收费结构、账单描述和账户地址等体验。on_behalf_of 不应当被当成只改账单文字的显示开关，它可能影响支付的业务归属、费用和结算行为，需结合国家和账户政策评估。

退款通常先从平台余额扣除。平台可以尝试通过 transfer reversal 向 connected account 收回已转资金，但这不等于任何情况下都能保证收回；卖家余额不足时可能发生错误或后续负余额问题。平台需要明确退款准备金、卖家追偿机制和争议责任条款。

## Separate charges and transfers：先收费，再按业务决定拆款

Separate charges and transfers 同样先在平台账户上创建 charge，但平台将资金转往 connected account 的操作与 charge 分开。它适合一笔订单涉及多个 connected accounts、付款时接收方还未确定、需要在付款后再计算分账，或需要先付款后转账的业务。

例如，一个购物车包含多家商户的商品，平台要把收入拆成多个转账；外卖订单需要分别结算餐厅和配送人员；服务平台可能先收取客户付款，完成排班后再确定具体服务提供者。与 Destination charge 的“为一个明确卖家立即转款”相比，Separate charges and transfers 提供更灵活的时间和一对多、一对一或多对一资金关系。

灵活性伴随更复杂的资金管理。Stripe 文档指出，平台账户承担 Stripe 费用、退款和争议扣款；平台需要在余额中有足够资金来执行转账。有些用例下，转账金额可以高于关联 charge，或者在支付资金可用前就发生转账，平台必须监控余额，避免出现无法覆盖的资金缺口。可以将 transfer 与 charge 关联，使转账在相关资金可用后再发生，但具体时序仍应按 API 和账户规则配置。

Separate charges and transfers 不是“任何平台默认都更好”的选项。它需要更复杂的对账、退款转回、资金状态和 connected account 关联处理。只有业务确实需要多方拆账、延后确定受款人或独立安排转账时，才应选择这种模式。

## 退款、争议和费用承担差异

选型时要把退款和拒付流程一起画进资金流图。Direct charge 的退款和争议金额通常先影响 connected account 余额；Destination charge 和 Separate charges and transfers 则由平台余额承担相关扣款。若客户向平台客服申诉退款，平台内部可以再按合同与卖家追偿，但 Stripe 账面扣款账户遵循 charge type 和账户设置。

在 Destination charge 或 Separate charges and transfers 中，平台可以尝试 reversal 已转给卖家的款项以收回退款或争议成本。Connected account 余额可能不足，反转失败或导致负余额。是否可以进一步从外部账户扣款取决于 connected account 的配置和 Stripe 规则，不能把对卖家的追偿视为自动必然成功。

Stripe 费用也要单独核实。Direct charges 在适用配置下可选择由 connected account 或平台承担费用；Destination charges 和 Separate charges and transfers 通常在平台账户使用平台定价并承担费用。使用 on_behalf_of 时，connected account 所在国家可能影响平台承担的特定费用。不同市场、支付方式及合同价格可能产生差异，商业报价和财务模型应按实际账户费率计算。

## 客户账单和记录商户设置

支付对象在哪个账户创建，以及是否设置 on_behalf_of，会影响客户在银行或账单记录上看到的平台或 connected account 信息。客户认不出账单描述，可能以为遭遇陌生扣款并提出拒付。账单展示应与网站品牌、收据、订单确认和客服说明一致。

在统一平台品牌的产品中，需明确由平台还是卖家作为 customer-facing business。若通过 on_behalf_of 让 connected account 成为记录商户，确认该账户名称、地址和联系方式已正确设置。若客户主要认知的是平台，但账单出现卖家名称，必须在购买流程中解释这一关系。

charge type 还会影响用户账户中支付方式设置的来源。官方文档说明，不同 direct/indirect charge 方案会使用平台或 connected account 的付款方式配置。要根据业务决定谁能启用哪些支付方式，避免客户看到平台允许、卖家账户却无法处理的结账选项。

## 选型决策表

| 业务问题 | Direct charge | Destination charge | Separate charges and transfers |
| --- | --- | --- | --- |
| 付款创建在哪个账户 | Connected account | 平台账户 | 平台账户 |
| 典型接收方数量 | 单个卖家 | 单个卖家 | 可多个 connected accounts |
| 何时确定受款方 | 创建付款时 | 创建付款时 | 可在之后确定 |
| 退款/争议主要扣款账户 | Connected account | 平台 | 平台 |
| 适合场景 | 卖家直接面向客户，平台提供软件能力 | 平台收款并立即向单一卖家分配资金 | 多方拆分、延后确定受款人或独立转账 |
| 实施复杂度 | 相对直接 | 中等 | 较高，需要管理独立转账和余额 |

这个表是高层决策辅助，不代替国家、账户类型、支付方式、税务、合规及合同责任审查。实际可用能力以 Stripe 当前账户配置为准。

## 上线前需要回答的工程问题

**对象归属：** PaymentIntent、Charge、Refund、Dispute 和 Transfer 分别属于平台账户还是 connected account？Webhook 事件如何将账户上下文映射到内部订单？

**客户体验：** 客户在账单上看到谁的名称？客服由平台还是卖家承担？退款沟通能否明确告知实际处理方？

**余额与风险：** 若平台先承担退款或争议，是否有资金储备？卖家余额不足时如何处理 transfer reversal？对负余额和追偿是否有书面合同流程？

**分账模型：** 一笔订单能否涉及多名受款人？平台何时知道具体卖家？是否需要在 charge 与 transfer 之间等待履约、退款窗口或服务结算？

**测试覆盖：** 逐一测试 Direct、Destination 和 Separate charges and transfers 的成功付款、部分退款、全额退款、connected account 余额不足、争议扣款、transfer reversal、账户地区限制和账单描述。

## 常见问题

### 一个 Connect 平台只能选一种 charge type 吗？

不一定。平台可以在不同业务流程中使用多种模式，但每条流程要明确账户上下文、退款责任、费用承担及对账方式。尽量避免同一产品中不必要地混用导致客服和财务难以判断资金归属。

### Destination charge 能给多个 connected accounts 分账吗？

Destination charge 主要用于向一个已知 connected account 转款。如果一笔客户付款需要拆到多个 connected accounts，或接收方要在后续确定，通常需要评估 Separate charges and transfers。

### 平台余额为什么被退款或拒付扣款？

如果支付是在平台账户创建的间接收费模式，平台余额可能承担退款与争议相关扣款。平台可按适用方案尝试反转 connected account transfer，但需要处理卖家余额不足和资金追偿风险。

### on_behalf_of 只是用于显示卖家名称吗？

不是。Stripe 文档说明它还可能影响结算国家、定价、账单描述、账单地址和 payout 延迟等行为。配置前要结合账户所在地、法律关系和付款方式评估。

## 总结

Stripe Connect 的收费方式会决定资金在哪里创建和分配，也会决定客户看到谁、费用从哪里扣、退款与拒付由谁先承担。Direct charge 更贴近卖家直接交易；Destination charge 适合平台为单个卖家收款并立即分配；Separate charges and transfers 适合需要多方拆款或延后转账的复杂市场。

先从业务合同、资金流和争议责任确定模式，再设计 API 调用和 Dashboard 配置。对间接收费模式，应把平台余额、退款、争议、transfer reversal 和卖家负余额纳入财务预案。更多细节请参考 [Stripe Connect 收费类型与资金流](https://docs.stripe.com/connect/charges)、[Destination charges](https://docs.stripe.com/connect/destination-charges) 和 [Separate charges and transfers](https://docs.stripe.com/connect/separate-charges-and-transfers)。
