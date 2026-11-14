---
title: "Stripe Invoice 作废与坏账处理：void 和 uncollectible 状态区别"
date: 2026-11-14
description: "区分 Stripe Invoice 的 void 与 uncollectible 状态，说明各自适用场景、PaymentIntent 影响、webhook 同步及与 credit note、退款的关系。"
slug: "stripe-invoice-void-vs-uncollectible-accounting-guide"
tags: ["Stripe", "Invoice", "账务", "坏账"]
keywords: ["Stripe Invoice void", "Stripe uncollectible 发票", "Invoice 作废和坏账区别", "Stripe invoice.marked_uncollectible", "Stripe 发票账务处理"]
---

# Stripe Invoice 作废与坏账处理：void 和 uncollectible 状态区别

发票开出后，客户可能取消订单、拒绝付款、长期失联，或发现发票金额录错。Stripe Invoice 提供 void 和 mark_uncollectible 等处理方式，但它们代表不同的业务事实。Void 表示这张发票不再作为应收款追收；uncollectible 表示商家把未收回的应收账款标记为无法收取或坏账处理。两者都不是“客户已经付款”，也不能和退款混用。

Stripe Invoice 的状态包括 draft、open、paid、uncollectible 和 void。Invoice 关联的 PaymentIntent 在发票定稿时创建；Stripe 文档指出，void Invoice 会取消关联的 PaymentIntent。标记为 uncollectible 常用于坏账的账务跟踪。具体操作是否可用受发票当前状态和 API 条件影响，应先检索对象并确认再执行。[Invoice 对象 API](https://docs.stripe.com/api/invoices/object)；[标记 Invoice 为坏账](https://docs.stripe.com/api/invoices/mark_uncollectible)；[作废 Invoice API](https://docs.stripe.com/api/invoices/void)。

## Void：发票不再应收

Void 通常适用于发票本身不应继续存在为待付款要求的情形，例如重复开票、订单取消、开票对象或客户信息错误，或商家确认不再要求客户支付该账单。作废后，Invoice 状态成为 void，相关付款意图会被取消，发票不再按普通 open 状态收款。商家应保存作废原因、操作时间和授权人，避免财务团队误把它当作已支付。

Void 不等于退款。如果原发票已经付清，不能通过作废发票来替代退款交易；应按实际支付状态使用 Stripe Refund 和必要的 Credit Note 流程。若发票尚未支付但商品已经部分交付，则还需确认会计、税务和合同上该如何更正，不能只看技术上是否能调用 void endpoint。

定稿的发票可能已经发送给客户并成为正式账务记录。作废时需要同步客户通知、订单状态和会计系统，说明原发票已失效以及是否会重新开具。不要直接删除业务数据库里的发票行，因为审计需要保留原 Invoice ID、number、voided_at 和原因。

## Uncollectible：将未收回债款标记为坏账

mark_uncollectible 用于记录发票无法收回或按商家会计政策作为坏账处理。它不是付款操作，也不是把 Invoice 的金额改为零。Invoice 仍保留总额、税额、余额与状态转换时间，以便账务与收入报告了解这笔应收款曾经存在但未收回。

在决定标记前，先检查催收流程是否结束、客户是否提出争议、是否有后续支付计划或新的付款方式。对仍有合理可能收款的 open Invoice，过早标为坏账会影响财务报表和催收任务。此类状态转换应由有权限的财务角色执行，并记录内部审批或坏账原因。

标记 uncollectible 后，客户以后主动补款的处理方式应按当前 Stripe Invoice 允许的状态与业务财务流程决定，不应假定它会自动回到正常 open 状态。需要重新收费时，应基于当前 API 状态创建适合的新收款流程或由财务确认后执行，不要绕过状态校验直接尝试扣款。

## 与 Credit Note 和退款的关系

Credit Note 用于更正或冲减已定稿发票的金额，例如发票商品数量、服务范围或税额需要调整。它会保留原发票与更正单据之间的关系，适合账单调整和会计记录。Refund 则是将已收取的资金退还给客户的资金动作。Void 是让发票失效；Uncollectible 是标记债务不可收；Credit Note 是账单金额调整；Refund 是返还已收款。业务决策应先判断实际发生了哪种情况，再选择对应对象。

例如客户已经支付后订单取消，通常需要评估退款和 credit note，而不是把 Invoice 标成 void 来掩盖退款；客户从未付款且本来不应开票，可能适合作废；客户确实获得了服务但无力或无法付款，可能由财务将未收款标记为 uncollectible。不同国家的发票更正要求并不相同，账务与税务处理需由商家专业人员确认。

## 操作前的状态检查

所有变更都从服务端读取 Invoice 最新对象开始。确认 Invoice ID 属于当前客户和正确 Stripe account，检查 status、paid、amount_remaining、payment_intent 和 subscription 字段。若 Invoice 仍是 draft，编辑或删除草稿可能比 void 正式发票合适；若已经 paid，先确认 Refund 和 Credit Note 的适用流程；若已经 void 或 uncollectible，则不能把相同操作重复执行当作幂等成功。

一个可靠的客服操作页应显示：发票编号、客户、总额和已付金额、剩余金额、账期、关联 Subscription、PaymentIntent 状态、可用操作和警告。提交前让操作者选择原因和确认影响。服务端不能只相信浏览器传入的 status；必须再检查权限、对象状态和可执行条件。

## Webhook 与账务状态同步

Invoice 状态变化会产生相关事件，例如 invoice.voided、invoice.marked_uncollectible、invoice.paid 或 invoice.payment_failed。Webhook 要验证签名、按 event ID 去重并记录处理历史。收到事件时以 invoice ID 查找本地账单，再从 Stripe 获取当前状态或按事件版本处理，避免乱序事件覆盖本地较新的结果。

本地订单状态和 Stripe Invoice 状态应分开保存。作废发票不一定代表整个订单取消；坏账也不一定代表服务立即关闭；Invoice paid 可能来自卡支付、Customer balance 或人工 out-of-band 标记。业务规则需要另行决定履约、权限和催收状态。

使用 Stripe Revenue Recognition 或外部会计系统时，确认 void 和 uncollectible 对报表的影响。跨系统同步时保存原始事件 ID、Invoice ID、变化前后状态、操作人和会计参考号，以便期末对账。

## 测试和常见误区

在测试模式验证 draft、open、paid、void 和 uncollectible 可能的状态转换。确认 void 后关联 PaymentIntent 及客户可见发票页面的变化；确认 uncollectible 仍保留金额信息并触发正确的财务流程。还应测试重复 webhook、权限不足、过期页面重复点击和客服操作时 Invoice 已被其他操作更新的情形。

常见错误包括：把 void 当作退款、把 uncollectible 当作优惠抵扣、把标记坏账当作订单支付成功、在客户已经付款后重新创建一张完全相同的账单、或在更新失败后让前端直接覆盖本地账单状态。通过服务器端状态检查和事件对账可以避免这些问题。

## 上线检查清单

- Void、uncollectible、credit note 和 refund 在界面和财务操作说明中清楚区分。
- 操作前读取 Invoice 最新状态并确认 Customer 与 Stripe 账户归属。
- Void 时保留原因、操作者、时间及重开/重新开票关联。
- Uncollectible 需要财务权限和业务依据，不能当作普通支付失败按钮。
- 已支付发票按退款和更正流程处理，而非直接作废。
- Webhook 验签、去重，处理 Invoice 状态的重复和乱序事件。
- 本地履约和客户权限不由 Invoice 状态单字段自动决定。
- Stripe 报表、收入确认和会计系统能追溯发票最终处置。
- 测试对象状态不合法时，前端能解释并刷新当前状态。

## 总结

Stripe Invoice 的 void 和 uncollectible 表达不同财务事实。Void 让一张不应继续追收的发票失效；uncollectible 保留发票金额并标记未收回的应收款。它们都不同于退款或 credit note。操作前核对发票当前状态和收款情况，保留审计链路，并将 Stripe 事件、订单履约与会计处理分别同步，才能避免用一个状态掩盖真实交易。

本文用于工程实现参考，不构成会计或税务建议。实际坏账和发票更正规则请结合商家账务政策及所在地要求确认。
