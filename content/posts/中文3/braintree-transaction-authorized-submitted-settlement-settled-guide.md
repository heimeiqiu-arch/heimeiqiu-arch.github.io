---
title: "Braintree 交易显示 Authorized 但商户没收到钱？看懂提交结算与 Settled 状态"
date: "2026-11-23T23:59:00+08:00"
slug: "braintree-transaction-authorized-submitted-settlement-settled-guide"
description: "Braintree 商户交易停在 Authorized 时，客户账单可能只有授权保留；收款需提交 settlement，经历 Settling 到 Settled 后才进入商户账户并转往银行。本文说明状态含义和 void、refund 的区别。"
keywords: ["Braintree transaction authorized not settled", "Braintree submitted for settlement status", "Braintree transaction settled merchant bank", "Braintree settlement declined", "Braintree Authorized 没收到款", "Braintree 交易提交结算"]
tags: ["Braintree", "支付网关", "商户结算", "交易状态"]
categories: ["支付问题"]
---

在 Braintree Control Panel 中，交易显示 Authorized（已授权）时，商户可能会看到客户银行卡出现一笔 Pending（待处理）金额，但商户尚未收到这笔销售款。Braintree 官方说明，授权只表示发卡机构同意暂时保留相应资金；要收取款项，交易还需要提交 settlement（结算）。提交后可能依次显示 Submitted for Settlement、Settling，最后变为 Settled。交易授权、资金捕获、进入商户余额和银行打款是不同节点，不要把客户账单上的待处理金额当作商户已收款。

本文针对 Braintree 商户交易生命周期和状态排查，不是消费者银行卡退款指南。具体交易如何自动提交结算、是否需要商户手动操作，取决于交易创建方式、SDK/Control Panel 设置、支付方式及账户配置。请以 Braintree 当前控制面板、开发者文档和实际交易历史为准；不同处理器的 Settlement 时间可能不同。

## Authorized：授权通过，但资金尚未捕获

当买家提交付款后，Braintree 会向相关处理器发起授权。如果银行批准，交易可能显示 Authorized。Braintree 官方生命周期文档解释，此时资金是在买家账户中被暂时保留，但还没有真正移除；商户也不能据此认为销售款已经进入商户账户。

若商户计划马上收款，需要根据现有集成流程将授权提交结算。部分交易通过默认设置在创建时就提交，其他交易可能由商户在发货后再捕获。先查看交易记录是否设置了提交结算，以及后台是否出现操作失败或需要进一步处理。对实体商品，商户是否先发货再捕获应符合自己的订单和风险流程，不能把不同商户的做法当成强制规则。

授权停留太久可能变为 Authorization Expired（授权过期）。Braintree 文档说明，授权有效时间会因支付工具、交易类型和商户类别而异，不存在适用于所有交易的统一天数。查看该笔交易的授权日期与状态，避免照搬网上其他银行卡类型或国家的时限。

## Submitted for Settlement 与 Settling 有什么区别

Submitted for Settlement（已提交结算）表示 Braintree 已开始收取资金的流程，交易已进入待处理结算批次；它不等于资金已经抵达商户的银行账户。Braintree 官方说明，结算通常按夜间批次处理，具体时间取决于处理器。商户可以在控制面板中确认交易是否已经提交，并查看随后状态变化。

Settling（结算中）是 Braintree 与处理器沟通结算请求时的过渡状态。官方文档指出，这个阶段持续多久取决于处理银行。如果交易停留在 Settling，记录交易 ID、支付方式和时间，按商户账户的处理安排观察；超过账户页面说明的时间后，再通过 Braintree 支持询问处理器返回信息。不要因为状态不是 Settled 就再次创建一笔相同金额的销售。

Settled（已结算）表示资金已进入商户账户的处理流程。Braintree 官方生命周期说明，交易显示 Settled 后，资金会进入商户账户并被路由到银行账户。商户接下来需要核对商户余额、银行打款计划和银行账单，而不是把交易页面的 Settled 当作银行已完成入账的证明。

## Processor Declined、Gateway Rejected 和 Failed

Processor Declined（处理器拒绝）表示发卡机构或支付处理器未批准交易。商户应查看适用的拒绝原因和客户可见提示，并通过合规方式让客户选择其他付款方式或联系发卡行。不要在未获得客户同意时反复尝试多笔相同金额的卡付款。

Gateway Rejected（网关拒绝）可能与地址验证、CVV、重复交易、风控阈值或账户处理限制有关。Braintree 状态文档列出这些可能原因，具体原因应查看交易的 processor/gateway response 字段或 Control Panel 详情。不要为了绕过风控降低安全设置或要求客户把完整卡号、CVV 发到客服消息中。

Failed 表示交易发送给处理器时发生错误。先确认该交易有没有生成有效的授权或其他后续状态，再依据响应内容排查。若后台出现重复请求，使用交易 ID、订单 ID 和幂等处理记录判断是否实际上创建了另一笔交易。

Settlement Declined（结算被拒）表示处理器拒绝了销售款结算或退款请求，交易未成功完成结算。Braintree 官方说明，这种状态较少见，可能只影响特定类型的交易；查看处理器返回码，并按 Braintree 文档或支持建议联系相应服务方。商户不要仅凭初始授权成功就交付高价值商品。

## 什么时候应该 Void，什么时候应该 Refund

如果交易只是 Authorized，且商户不再打算收款，通常需要检查是否可以 Void（作废授权），以避免继续等待不必要的资金保留。Braintree 官方状态说明，Authorized 状态可以作废。提交结算后，在部分状态下仍可能作废，但必须以交易当前状态和页面提供的操作为准。

如果交易已经进入 Settling 或 Settled，Braintree 状态文档说明不能再以 Void 取消；此时应按正确流程提交 Refund（退款）。Void 是阻止仍未完成的授权或结算，Refund 是在资金已进入结算后返还款项，两者不等同。选择操作前打开原交易记录确认状态、是否已有退款和退款是否在处理中，避免重复退款。

对于 PayPal 等特定支付方式，Braintree 部分状态和可执行操作可能不同。不要把银行卡交易的 void/refund 规则直接套到所有交易类型；以该笔交易详情的可用操作、开发者文档和支付方式条件为准。

## 商户如何排查一笔交易卡住

先记录 Transaction ID、订单号、金额、币种、支付方式、授权时间和当前状态。若状态 Authorized，检查是否提交过结算；若 Submitted for Settlement 或 Settling，检查交易是否已进入批次，以及处理器是否仍在返回结果；若 Failed 或 Settlement Declined，查看响应码并联系相应支持。每一步都应在同一交易记录中跟踪，避免重复收款。

若客户账单出现授权但 Braintree 仍未显示结算，向客户解释授权与正式扣款不同，并让其通过自己的发卡行询问具体授权记录。商户不能控制银行显示或释放授权的时间。若 Braintree 交易已 Settled 但银行款未显示，继续查看商户账户打款记录和银行日历，按商户收款账户路径调查。

### Braintree 状态排查清单

1. 在 Control Panel 打开原交易，核对 Transaction ID、金额、币种和最新状态。
2. Authorized 代表资金可能只被暂时保留；检查是否需要提交结算。
3. Submitted for Settlement 表示已进入结算流程，不等于银行到账。
4. Settling 是处理器沟通中的过渡状态，时长取决于处理银行。
5. Settled 后再核对商户余额和银行打款，不要重复创建订单。
6. Gateway Rejected、Processor Declined 或 Failed 时，查看具体响应代码和拒绝原因。
7. 未结算的交易按状态评估 Void；已 Settled 或 Settling 则查看 Refund 选项。
8. 保存交易编号和支持案例号，不向买家索要完整卡号或安全码。

如果你正在评估在线商户收款服务，可点击下方按钮查看 CBPayments。Braintree 交易状态和 CBPayments 产品规则互不替代；CBPayments 的支付方式、覆盖地区、结算安排和费用请以官方信息及商户协议为准。

{{< cbpayments-button >}}

## 总结

Braintree Authorized 只表示付款授权，不表示商户已收款；商户还需依据集成配置将交易提交结算。Submitted for Settlement 与 Settling 表示结算流程正在推进，Settled 才代表交易已进入商户结算记录，之后仍需核对银行打款。确认状态后再选择 Void 或 Refund，避免重复扣款或退款。每个处理器、支付方式和账户的时限都可能不同，最终以 Control Panel 交易详情及 Braintree 官方文档为准。

## 官方参考资料

- [Braintree：交易状态说明](https://developer.paypal.com/braintree/docs/reference/general/statuses/)
- [Braintree：交易生命周期](https://developer.paypal.com/braintree/articles/get-started/transaction-lifecycle)
- [Braintree：Transaction 对象与状态字段](https://developer.paypal.com/braintree/docs/reference/response/transaction/php)
