---
title: "Stripe Swish 瑞典支付：BankID 授权、三分钟超时与退款追踪"
date: 2026-11-15
slug: "stripe-swish-sweden-bankid-qr-timeout-refund-reference-guide"
description: "Stripe Swish 面向瑞典消费者的手机与桌面二维码支付流程、SEK 金额边界、三分钟授权时限、商户展示规则和退款状态核对。"
keywords:
  - Stripe Swish 支付
  - Swish Stripe 接入
  - Swish BankID 付款
  - Stripe Swish 退款
  - Swish payment_reference
tags:
  - 支付方式
  - 瑞典
---

Swish 是瑞典常用的移动支付方式，客户通过 Swish App 和 Swedish BankID 授权付款。桌面用户扫描结账页面的二维码，移动用户通常跳转到 Swish App，再返回商家页面。Stripe 会立即通知商家付款成功或失败，但客户需要在有限时间内完成授权。若支付过期，PaymentIntent 会回到需要付款方式的状态，用户必须重新发起支付。

Stripe Swish 还有一个容易被忽略的展示特点：Stripe 作为 merchant of record，客户在 Swish App 和银行账单中会看到 Stripe 的名称；商家名称会显示在 Swish 的消息字段。普通 statement descriptor 设置不能完全控制这些展示字段。本文梳理资格、授权时限、退款和 reference 对账，帮助商家正确设计瑞典结账体验。

## 账户资格和交易边界

Swish 面向瑞典客户，展示币种为 SEK，Stripe 文档当前列出单笔最低 3 SEK、最高 150,000 SEK。商户账户可以位于多个支持国家，但具体账户仍需符合支付方式资格；消费者在瑞典、账户资格符合和交易币种匹配都需要同时检查。账户可能还需要遵守行业限制，并接受 Stripe 或 Swish 相关审核。

Swish 是一次性支付方式，不支持 recurring、SetupIntent、保存后 off-session 扣款、手动捕获或部分捕获。Checkout 不支持 Swish 的 subscription mode 或 setup mode。订阅产品应提供支持周期扣款的支付方式，不能因为 Swish 在某一次付款中成功就尝试未来自动扣款。

当前官方页面标注 Swish 的访问可能需要请求 access。启用前查看 Payment Method Settings 和法律条款，确认账户实际已获准，再在测试环境验证端到端流程。资格状态、产品支持与行业清单可能发生变化，不能只依赖文章或其他商户的接入经验。

## 手机跳转与桌面二维码

手机用户从商家页面跳到 Swish App，使用 BankID 认证并批准付款；桌面用户扫描二维码后在手机 App 中授权。客户必须在三分钟内完成操作。超时后 PaymentIntent 会变为 requires_payment_method，不能继续展示旧的授权页面并期待客户之后完成。

移动端应配置好返回网站或应用的链接，让客户授权后回到对应订单详情。桌面端页面保持二维码和清晰倒计时，过期后提示重新开始。创建新的支付尝试前，先查询旧 PaymentIntent 状态；客户可能已经成功支付，只是浏览器返回失败。通过服务端确认后再创建新尝试，避免重复收款。

## PaymentIntent 与 Webhook 状态处理

服务端创建 PaymentIntent 时保存内部订单号、金额、SEK 币种和付款尝试 ID。浏览器接收 Stripe 发布的必要客户端信息并呈现 Swish 流程，但不应直接控制最终订单状态。Webhook 到达后先验证签名、记录 Event ID，再查找最新 PaymentIntent 状态并核对金额、币种和订单关系。

付款成功后，PaymentIntent 状态为 succeeded，可触发履约；失败或超时则标记为可重试或待客户处理。对重复 Webhook 使用事件 ID 和订单级幂等键，防止重复发货。若页面已经显示失败但服务器事件显示成功，以 Stripe 对象和内部订单当前状态为准，并安全地补跑未执行的履约任务。

## 退款支持与状态跟踪

Stripe 官方 Swish 页面列出全额和部分退款能力，退款期限为原付款后 365 天。退款通常需要几分钟，但 Stripe 会跟踪 Swish 的异步结果。总退款金额不能超过原支付金额；多笔部分退款要在内部账本累计校验，避免客服或后台工具超额退款。

创建 Refund 后，不要立即把客户到账标为完成。监听 refund.updated 和 refund.failed，或在 Dashboard/API 查询 Refund 对象状态。succeeded 表示 Stripe 收到最终退款成功结果；failed 时 Stripe 会将资金返回 Stripe 余额，商家需要通过其他方式退款。退款请求、最终处理、客户通知分开记录；退款失败应自动产生人工跟进任务。

由于 Swish 是付款钱包而非银行卡，客户可能在 Swish App 或银行账户中看到退款。客服应告知原支付订单和退款日期，若需要进一步查询，可使用 Stripe 退款记录和 reference 关联支付。不要用银行卡退款的统一到账时间承诺替代支付方式说明。

## 付款 reference 和商户名称

在 Swish App 中，Message 字段通常自动设置为商家名称：Stripe 优先使用法律实体名，必要时回退到可展示的商户名。对于 Swish 支付，Stripe 作为 merchant of record，会显示为 Swish 付款接收方并出现在客户银行账单描述中；商家业务名称则出现在消息字段。客户看到 Stripe 名称时，不一定代表付款发错账户。

商家可通过 payment_method_options[swish][reference] 设置单笔付款参考，允许 1 到 35 个字母、数字或连字符。这个自定义 reference 与支付提供方返回给 Stripe 的银行参考不是同一值。付款完成后，可以展开 PaymentIntent 的 latest_charge，读取 payment_method_details.swish.payment_reference。将这两个 reference、PaymentIntent ID 和内部订单号分别保存，避免把自定义参考误当成银行流水唯一编号。

通用 statement descriptor 和 Connect 的商户名称规则，不会覆盖 Swish 的 message 字段或 PPRO reference 映射。上线前在测试交易里检查客户在 Swish App 和银行账单可能看到的名称，并在订单确认邮件中解释支付收款方显示 Stripe 的原因。

## Connect 平台核对

Stripe Connect 可以处理 Swish 付款，支持 direct、destination 以及 separate charges and transfers 等适用模式。平台需要确认账户 capability、责任分配和 merchant of record 展示。某些平台结算安排中 Stripe 仍作为支付接收方，商家名称在 Message 字段呈现；不要假设与信用卡的 statement descriptor 完全相同。

平台订单和资金模型应分别记录平台订单、connected account、PaymentIntent、Charge、应用费、Transfer 和 payout。客户看到的名称与资金最终进入哪个 Stripe 账户是相关但不同的概念。财务对账根据 Stripe 对象和 Swish payment_reference 匹配，不要以客户看到的消息字段代替支付 ID。

## 常见问题排查

**客户授权后回不到商家页面。** 查询 PaymentIntent 和 Webhook，检查移动深链或 return URL。若支付已成功，安全更新订单；不要基于页面回调失败就重复扣款。

**二维码三分钟后过期。** 读取 PaymentIntent 状态，旧状态为 requires_payment_method 时创建新的付款尝试和二维码；若已成功，不要再收款。

**客户在账单里只看到 Stripe。** 这是 Swish 付款的 merchant of record 展示规则之一。用订单通知、Swish message 中的商家名称和 Stripe reference 帮助客户识别。

**设置的 reference 和客户银行流水不一样。** 自定义 reference 与 payment provider 返回的 payment_reference 不同，分别查询并记录。

**退款已提交但仍 pending。** 查询 Refund 对象和 Webhook 最终状态；退款是异步处理，只有 succeeded 才标记为成功，failed 时按其他方式退还。

## 上线前验证清单

验证账户获准、瑞典客户与 SEK 币种、3 至 150,000 SEK 金额边界、手机深链、桌面扫码、三分钟超时、Webhook 重试、全额退款与多次部分退款。检查 Swish App 的商户名、Stripe 作为收款方的提示、自定义 reference 和返回的 bank reference。为客户准备付款失败、过期和退款失败的支持流程。

Swish 的集成要同时处理手机授权体验和服务端状态，并解释清楚客户看到的收款方名称。用短时二维码或跳转授权提升付款体验，以 PaymentIntent 和 Webhook 为订单事实来源，再通过 Refund 和 payment_reference 完成售后和对账，能减少误判和重复操作。

## 官方资料

- [Stripe：Swish 支付](https://docs.stripe.com/payments/swish)
- [Stripe：Swish 收款接入](https://docs.stripe.com/payments/swish/accept-a-payment)
- [Stripe API：退款对象](https://docs.stripe.com/api/refunds/object)
- [Stripe API：PaymentIntent 对象](https://docs.stripe.com/api/payment_intents/object)
- [Stripe：Connect 费用类型](https://docs.stripe.com/connect/charges)
