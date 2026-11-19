---
title: "Stripe 卡片付款被拒怎么查？Decline Code 与重试处理指南"
date: 2026-11-19T20:20:00+08:00
slug: stripe-card-decline-codes-troubleshooting-guide
description: "Stripe 卡片付款失败时，如何在 Dashboard 和 PaymentIntent 中查看 decline_code，区分资料错误、余额不足、认证要求和泛化拒绝。"
keywords:
  - Stripe 卡片付款被拒
  - Stripe decline code
  - Stripe card_declined 怎么处理
  - Stripe PaymentIntent 付款失败
  - Stripe 付款重试规则
tags:
  - Stripe
  - PaymentIntent
  - 付款失败
categories:
  - 跨境支付
---

通过 Stripe 收款时，卡片付款失败可能在 Dashboard 或 API 返回中显示 card_declined、generic_decline、insufficient_funds、incorrect_number 或 authentication_required 等拒绝代码。代码有助于识别问题类型，但不一定能透露发卡行的完整风控理由。商家应区分客户可自行修正的卡片资料、需要银行确认的授权拒绝，以及需要 3D Secure 的认证问题，再决定是否重试。

“Stripe 卡片付款被拒怎么查”“Stripe decline code 怎么处理”“PaymentIntent 付款失败”是开发者和商家常见问题。Stripe 官方说明，发卡行自动系统会根据余额、消费模式、卡片资料等信号决定是否授权；Stripe 只会分享发卡行提供的部分信息。很多拒绝属于泛化类型，具体原因只有持卡人的银行能向持卡人解释。

## 在 Stripe 查看拒绝代码

在 Stripe Dashboard 中打开相关 PaymentIntent 或付款记录，查看付款尝试、错误信息和卡片结果。API 集成中可检查 PaymentIntent 的 last_payment_error 相关字段，读取 decline_code 和可用的网络拒绝信息。字段是否存在取决于错误类型和支付流程，不要假设每次失败都有同样的代码。

对同一 PaymentIntent 的多次确认尝试，应按时间和状态逐条查看。不要只根据订单数据库的一个“失败”标志判断，因为用户可能更新卡片、完成认证或再次提交。把 Stripe 对象 ID、请求 ID、时间戳和最终订单状态关联起来，方便排查重试与 webhook 更新。

拒绝代码反映的是发卡行或网络返回的信息，不能当成对客户的确定性指控。例如 generic_decline 往往不会给商家明确的银行原因；若卡片信息看起来正确，Stripe 官方建议让持卡人联系自己的发卡行了解详情。

## 常见 Stripe decline code 如何理解

### insufficient_funds：余额或可用额度不足

可能表示账户余额或信用额度不足以完成交易。让客户核实银行可用额度，或使用其他由商户支持的付款方式。不要让客户短时间连续重试同一张卡，因为多次授权尝试可能产生更多失败记录。

### incorrect_number、incorrect_cvc 或 expired_card：卡片资料有误

检查卡号、CVC 和到期日期是否输入正确，卡片是否已经更新或过期。让客户在安全的支付表单中重新输入资料，不要通过邮件、聊天或电话收集完整卡号和安全码。若卡片资料确定正确仍被拒，转向银行查询。

### do_not_honor 或 generic_decline：银行未提供具体原因

这类代码通常无法说明确切拒绝原因。不要推断为欺诈或卡片被封。可以提示持卡人联系发卡行确认是否需要批准交易、开启线上支付或完成验证。如果客户更新支付信息或确认银行授权后仍失败，停止重复尝试。

### authentication_required：需要认证或重新验证

该代码通常意味着需要额外身份认证，例如通过 3D Secure 完成验证。按 Stripe 付款流程发起适当认证，并检查支付结果是否成功回到商户页面。认证通过不代表发卡行一定授权；交易之后仍可能因额度、卡片设置或风险策略失败。

### lost_card 或 stolen_card：卡片被报告丢失或盗用

不要继续尝试这张卡，也不要建议用户绕过银行控制。请持卡人直接联系发卡行处理卡片安全问题，并按照商户政策选择其他有效支付方式。商家不应保存或传播敏感卡片资料。

### processing_error 或 issuer_not_available：处理或银行可用性问题

可能与网络、发卡行或处理环节暂时异常有关。查看 Dashboard 和 Stripe 状态通知，确认是否影响多笔交易。只有在确认前一笔没有成功、订单没有产生且 Stripe 建议允许重试时，才谨慎进行新的尝试。

拒绝代码含义会受卡组织、发卡行和集成方式影响。Stripe 官方文档可能列出代码的常见解释，但商户仍应参考当前 API 响应和 Dashboard，而不是仅凭代码对客户承诺付款一定会成功。

## 是否应该重试 Stripe 付款

首先确认该失败是否属于可修正问题。卡片号码或到期日期输入错误时，更新资料后进行一次新的尝试通常比不加区分地反复重试更有意义。需要银行批准时，让持卡人先联系发卡行。若错误提示要求认证，则完成认证流程后再依据 PaymentIntent 状态处理。

不要在短时间内自动重复发送大量相同授权。重复尝试可能增加客户银行的风控风险，生成多条失败事件，并让商户承担额外成本或造成客户困惑。针对可重试的临时错误，使用 Stripe 官方推荐的支付状态管理和幂等处理，确保同一业务订单不会因为网络超时创建重复付款。

对于订阅或自动扣款，重试策略应遵循 Stripe Billing 的状态和商户已向客户披露的账单规则。向客户发送明确通知，说明失败金额、下一步和如何更新付款方式；不要在未说明的情况下无限期重试。

## 商户排查 Stripe 付款失败的步骤

### 第一步：确认订单和 PaymentIntent 状态

查看 PaymentIntent 是否仍可操作、是否需要认证、是否已经成功或已取消。将 Stripe 对象与本地订单 ID 对应，避免把重复请求当成新订单。

### 第二步：检查 decline_code 与网络字段

读取 Dashboard 或 API 中提供的拒绝信息，记录其字段来源和时间。若只有 generic_decline，不要臆测银行内部理由；将持卡人联系发卡行作为下一步。

### 第三步：检查集成中的确认和 webhook 流程

确认前端是否收到需要认证的状态，用户完成验证后是否回到商户流程，以及后端是否正确处理 PaymentIntent 状态更新。不要只依赖浏览器跳转结果确认付款；服务器应按 Stripe 官方事件和对象状态更新订单。

### 第四步：安全地让客户修正资料或联系银行

让客户在 PCI 合规的支付表单中更新卡片信息，或联系发卡行确认授权。客服不要在聊天或邮件中索取卡号、CVC、密码或一次性验证码。

### 第五步：有必要时联系 Stripe 支持

如果 Dashboard 显示异常、同类付款大量失败或 API 错误与拒绝代码不一致，准备 PaymentIntent ID、请求时间、request ID 和可复现步骤，联系 Stripe 官方支持。不要提交不必要的客户敏感信息。

## 如何降低拒绝率并避免误导客户

支付页清晰展示金额、币种、账单频率和退款规则；卡片字段提供必要校验但不要把错误提示写成银行确定拒绝原因。对认证要求支持 Stripe 推荐的流程，并确保失败后客户知道下一步。监控支付成功率、拒绝类型和重复尝试，但对风控数据进行合规处理，避免储存不必要的敏感信息。

客服话术应区分“资料输入错误”“需要银行认证”和“发卡行拒绝授权”。如果没有具体原因，就明确告诉客户当前信息不足以确定拒绝细节，而不是猜测卡片风险。商家也不能保证更换卡片就能成功。

## 常见问题

### Stripe 的 generic_decline 表示什么？

这通常表示发卡行拒绝付款，但没有提供商家可见的具体原因。持卡人可联系发卡行确认。不要将该代码直接解释为欺诈或账户被封。

### card_declined 可以自动重试吗？

要先看具体失败原因、PaymentIntent 状态和 Stripe 当前建议。资料错误、认证要求和银行风控的处理不同。避免短时间不加区分地重复提交，防止产生多条授权和影响客户体验。

### 客户完成 3D Secure 后为什么仍失败？

3D Secure 是额外认证步骤，不是支付批准本身。认证完成后，发卡行仍可能拒绝授权。检查 PaymentIntent 最终状态，并让客户联系银行确认。

### 如何从 API 找到 decline_code？

查看 PaymentIntent 的 last_payment_error 等相关错误字段，具体结构取决于接口版本和失败状态。使用 Stripe 当前官方文档对照对象字段，并保护日志中的支付资料。不要记录完整卡号、CVC 或认证秘密。

## 总结

Stripe 卡片付款失败时，先从 Dashboard 或 PaymentIntent 查看 decline_code 和最终状态，再区分资料错误、额度不足、认证要求、银行泛化拒绝或临时故障。按对应原因让客户修正、完成认证或联系发卡行，避免无条件重复扣款。商户侧还要确保 PaymentIntent、webhook 和订单状态一致，并保护客户支付数据。

{{< cbpayments-button >}}

## 官方资料

- [Stripe：银行卡拒付与 decline code](https://docs.stripe.com/declines/card)
- [Stripe：处理认证要求的付款](https://support.stripe.com/questions/authenticated-payment-declined-with-an-authentication-required-decline-code?locale=en-GB)
- [Stripe：API 文档](https://docs.stripe.com/api/payment_intents)

本文为一般信息整理，不代表 Stripe、发卡行或卡组织的官方意见。拒绝代码、可重试性和接口字段可能随支付方式与 API 版本变化，请以 Stripe 当前 Dashboard 和官方文档为准。
