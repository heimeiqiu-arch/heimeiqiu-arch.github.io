---
title: "Stripe Billing Credits 与 Credit Grant：预付额度、促销赠额和发票抵扣"
date: 2026-11-14
description: "解释 Stripe Billing Credits 的 Credit Grant 状态、适用 Metered Price 的条件、抵扣顺序、到期管理及其与 Customer invoice balance 和 Cash Balance 的区别。"
slug: "stripe-billing-credits-credit-grant-prepaid-promo-guide"
tags: ["Stripe Billing", "Billing Credits", "Credit Grant", "Meter", "Invoice"]
keywords: ["Stripe Billing Credits", "Stripe Credit Grant", "Stripe 预付额度", "Stripe 促销额度", "customer invoice balance 区别"]
---

# Stripe Billing Credits 与 Credit Grant：预付额度、促销赠额和发票抵扣

按量计费的产品常见两种收费体验：客户先购买一笔额度，再逐步消耗；或者商家赠送一笔试用额度，让新用户体验服务。Stripe Billing Credits 可用于这类预付或促销用量额度，Credit Grant 对象记录分配给客户的 billing credits，并在符合条件时抵扣发票。它与 Customer invoice balance（客户发票余额调整）和 Cash Balance（银行转账资金余额）是不同的机制，不能因为它们都表现为余额就混为一谈。[Stripe Billing Credits 指南](https://docs.stripe.com/billing/subscriptions/usage-based/billing-credits)。

开始设计之前要确认账户当前能否使用 Billing Credits、适用的业务类型和 API 能力。Stripe 官方说明，Billing Credits 用于客户购买或获赠的用量服务额度，并有明确的允许与禁止使用场景。它不是通用储值钱包，也不用于向第三方付款或兑换礼品卡。实际商业模式、合同和地区规则仍应由业务与合规团队确认。

## Credit Grant 记录的是一笔额度分配

Credit Grant 表示发给某个 Stripe Customer 的 billing credit 额度。一个 Customer 可以有多笔 grant，例如一笔预付款、一笔新客试用奖励，以及一笔客服补偿额度。每笔 Grant 可设置金额、币种、适用价格范围、起效时间、过期时间、类别和内部 metadata。将每一笔额度拆开记录有助于追踪来源、活动、剩余余额和退款/补偿决策。

官方文档列出多种 Grant 状态：Pending 表示可用余额尚不可用；Granted 表示已按生效时间进入可用范围；Depleted 表示额度已经使用完；Expired 表示额度到期或被立即过期；Voided 表示未应用到任何发票的 grant 被作废。作废与过期的边界很重要：如果额度已经部分或全部应用到发票，就不能简单按未使用 Grant 的方式作废；已有应用记录需要通过支持的账务操作处理。

如果未设置 `effective_at`，grant 通常立即生效；未来生效的 grant 在生效前不可用。未指定 `expires_at` 时，额度不会因为某个应用界面上的“试用结束日期”而自动到期。促销活动需显式设置到期规则并向客户说明日期、时区和适用范围，后台也要确认 Stripe 实际对象的时间戳和状态。

## 抵扣只发生在符合条件的发票上

Billing Credits 不会直接把任意 PaymentIntent 金额改成零，也不是在 Checkout 页面使用的通用优惠券。Stripe 按 Credit Grant 与订阅发票条件应用额度。当前官方指南列出的主要条件包括：发票的 `period_end` 不早于 grant 的生效时间；若设置过期时间，周期结束时间需在过期时间之前；发票最终化时 grant 有可用余额；币种与发票币种一致。

此外，Billing Credits 仅可应用于通过 Stripe Billing Meter 记录用量的 metered subscription items。不能用于与订阅无关的一次性发票、订阅首账单中的一次性 invoice item、licensed 价格项目，或通过旧 Usage Records 上报的 metered 价格。套餐结构若同时含固定订阅费和按量项目，需要检查各发票行项目是否符合资格，不能认为整张发票的所有费用都会被额度抵扣。

官方文档说明，Credit Grants 在折扣之后、税费和 Customer invoice balance 之前应用。这个顺序会影响客户看到的账单金额和税额计算。实际应以发票行项目中列出的折扣、credit amounts、税和余额调整来解释最终金额，避免客服仅凭“grant 金额减去账单总额”猜测剩余额度。[抵扣资格与顺序](https://docs.stripe.com/billing/subscriptions/usage-based/billing-credits)。

## 与优惠券和客户余额的区别

Coupon/Promotion Code 通常用于折扣定价，例如对价格打折或减免某个周期；Billing Credit 则是按额度抵扣符合资格的计量用量发票。前者改变适用折扣，后者记录可消耗的 credit grant 和使用过程。若产品需要“前 1000 次 API 调用免费”，需要先确认用量价格、Meter 和 Billing Credits 的模式是否适合，而不能只用一个优惠券概念涵盖所有计量场景。

Customer invoice balance 记录客户发票余额上的调整，常见于账单抵扣或贷项处理；Cash Balance 持有银行转账收到的客户资金。Billing Credits 又是第三种结构，绑定于客户的预付/促销服务额度，并基于 Metered Price 等规则应用。API 对象和发票展示字段不同，因此本地数据库应将它们分开，不要放在单一的 `credit_balance` 列里。

如果客户通过 Stripe Invoicing 为预付额度付款，资金收取与 credit grant 分配是两步：第一步收取预付款并对账，第二步为对应 Customer 创建 Credit Grant。失败的预付款不能分配成功额度；重复 webhook 也不应重复发放 grant。可以把内部订单号、grant ID、付款对象 ID、金额币种和客户标识关联在账务系统中，形成审计链。

## 设计发放流程和幂等控制

在服务端实现授权后的 grant 创建流程。用户购买额度、客服赠额或活动奖励需要经过不同权限与审计策略。预付款额度应在实际付款达到业务定义的成功状态后发放；赠额则限制活动对象、次数、总额和有效期，防止客户端通过重复请求无限领取。

使用内部业务操作 ID 做幂等。比如一张预付款订单只允许对应一笔 grant；当创建 Grant 的 API 调用超时，服务端先查询是否已有对应 Grant，再决定是否重试。不要因用户刷新“支付成功”页面就再次创建 credit grant。为每笔 grant 保存来源类型、内部订单、Stripe customer、币种、原始金额、已应用金额、剩余额度和有效时间的映射，任何余额展示都应从可信账务来源同步，而不是浏览器本地累计。

如果需要纠正错误额度，先区分 grant 是否已应用到发票。尚未使用的 grant 可以根据当前 API 支持的作废流程处理；部分使用或已经消耗的额度需要检查发票和 credit balance transaction，再执行经审核的调整。直接删除本地 grant 行会让 Stripe 与应用账簿无法对账。

## 用量 Meter、发票和额度一起测试

在生产启用前，验证完整的用量计费链路：创建或配置正确 Meter；让订阅项关联 Metered Price；报告测试用量；创建符合币种、生效和有效期规则的 Credit Grant；再观察发票行项目实际抵扣。单独验证 Grant API 创建成功，只说明对象已创建，不证明未来每种发票都会符合抵扣资格。

至少覆盖以下情况：额度尚未生效、已过期、币种不同、余额不足、订阅只有 licensed 项目、同时有固定费和 metered 用量、折扣与税费并存、同一客户多笔 grant。检查发票最终化时间和周期 `period_end`，因为可用性取决于发票何时生成以及 grant 时间窗。

在 webhook 侧订阅适用的 Billing Credit Grant 与 credit balance transaction 事件，例如 grant 创建/更新和余额交易创建。处理事件时进行签名校验和 event ID 幂等；如需决定客户剩余额度，应读取 Stripe 的当前余额摘要或 grant 对象，不能用事件数量代替金额。对账时把每张 Invoice 的抵扣行与对应 credit balance transaction 关联起来。

## 常见问题与排查

**Credit Grant 已创建，但账单没有抵扣：**检查订阅项目是否是使用 Stripe Meter 的 metered Price，发票 `period_end` 是否在生效和到期范围内，币种是否匹配，以及发票最终化时是否仍有可用余额。若是 licensed 项目或旧 Usage Records，不符合当前指南列出的适用范围。

**额度和 invoice balance 显示不同：**它们本来就是不同机制。核对 Grant、credit balance transaction、Invoice line item 和 Customer invoice balance，确认页面展示的是哪一种余额。

**客户退款后还保留预付额度：**退款与 grant 状态不是同一对象。根据预付合同和已使用金额定义如何处理未使用余额，检查 Stripe 允许的 grant 变更操作和账务要求，并记录退款与额度调整的关联。

**相同活动额度被重复发放：**检查 webhook event 去重、内部订单唯一约束、API 超时后的补偿查询和后台人工重放操作。创建发放记录之前，应先按业务操作 ID 验证是否已存在 Grant。

**促销到期后客户仍看到额度：**检查 `expires_at`、实际时区和 grant 状态，确认当前 UI 显示的是可用余额而非原始额度。不要只依赖前端倒计时将额度视觉隐藏，后台应从 Stripe 和内部同步结果重新确认可用金额。

## 上线检查清单

- 已确认账户计划和当前 Stripe 配置支持所需 Billing Credits 能力。
- Credit Grant 与 Customer、来源订单、币种、适用价格和时间范围关联。
- 仅在符合条件的 Metered Price 发票上预期抵扣。
- Customer invoice balance、Cash Balance、coupon 与 Billing Credits 在数据模型中区分。
- 预付款在成功收款后才发放，赠额流程有额度与次数限制。
- 创建 Grant 和处理 webhook 都有幂等键及审计记录。
- 用量、折扣、税、invoice balance 和 credits 并存时做过发票验证。
- 退款、撤销、过期和部分消耗场景已有明确处理流程。
- 客户看到的剩余额度、到期日期与 Stripe 当前状态一致。

## 总结

Stripe Billing Credits 通过 Credit Grant 表示预付或促销用量额度，并按 Metered Price、币种、有效期和发票周期等条件抵扣订阅发票。它不同于折扣券、Customer invoice balance 和 Cash Balance。实现时应在服务端受控发放、做好幂等和审计，并通过真实测试用量与发票行项目核对抵扣结果。

Billing Credits 的可用性和具体 API 行为会随 Stripe 账户配置与产品版本变化。请以当前 Stripe 官方指南、API 响应和账户可用功能为准。
