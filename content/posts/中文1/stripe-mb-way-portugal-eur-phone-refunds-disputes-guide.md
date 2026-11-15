---
title: "Stripe MB WAY 接入指南：葡萄牙手机号、EUR 限额与争议"
date: 2026-11-15
slug: "stripe-mb-way-portugal-eur-phone-refunds-disputes-guide"
description: "介绍 Stripe MB WAY 的葡萄牙 B2C 客户、手机授权流程、EUR 交易与用户限额、单次支付限制、365 天退款和 7 天争议举证。"
keywords:
  - Stripe MB WAY
  - MB WAY Stripe 接入
  - 葡萄牙 EUR 支付
  - MB WAY 手机号付款
  - Stripe MB WAY 退款争议
tags:
  - Stripe
  - MB WAY
  - 葡萄牙支付
  - 数字钱包
---

MB WAY 是葡萄牙广泛使用的数字钱包支付方式之一。客户在结账时提供手机号码，然后通过 MB WAY 应用认证并批准付款。对希望向葡萄牙消费者销售的商家，这种以手机应用为核心的支付体验可以补充银行卡；但 MB WAY 是单次使用钱包付款，不能用于保存付款方式后自动扣款，且争议证据提交窗口较短。

接入时，商家不仅要检查 EUR 币种和 Stripe 账户资格，还需要区分商家单笔金额上限与客户自身的每日累计限额。本文介绍 MB WAY 的适用范围、手机号授权、集成限制、退款与争议流程，具体能力以 Stripe Dashboard 当前显示为准。

## 商家账户和客户资格

Stripe 当前文档列出多国商家账户可以接受 MB WAY 付款，客户使用国家为葡萄牙。账户类型支持 Merchant 和 Connect 平台，但业务模型只支持 B2C，不支持 B2B。商家账户可以注册在支持国家，不意味着非葡萄牙客户也能使用 MB WAY。

MB WAY 使用 EUR，单笔金额范围为 0.50 至 5,000 欧元。客户在 MB WAY 应用中的默认每日累计限额为 1,000 欧元，用户可以在应用中将其调整到最高 10,000 欧元。这个用户日限额和 Stripe 商家的单笔交易上限不是同一个设置，创建支付时需要分别考虑。

MB WAY 支持国际电话号码，但多数客户使用 +351 开头的葡萄牙号码。结账表单要使用适合国际号码的输入组件，不应将输入框限制为固定长度的葡萄牙号码。Stripe 的测试指南也提供专门的测试号码和跳转流程，正式上线前应按当前测试文档验证。

## 手机号与应用授权流程

客户在结账页选择 MB WAY 后，提供手机号码并在 MB WAY 应用中批准交易。Stripe 会即时通知商家付款是否成功。用户可能没有安装或登录应用、未收到通知、拒绝授权或中途离开；商家网站应在等待期间保持清晰的订单状态。

推荐流程是：

1. 用户选择 MB WAY 并输入手机号码；
2. 商家后端创建 Stripe Checkout Session 或 PaymentIntent；
3. Stripe 发起需要客户完成的授权流程；
4. 客户在 MB WAY 应用确认；
5. Stripe 通过服务端状态和 webhook 通知商家；
6. 商家确认成功后发货、发放数字权益或更新订单。

成功页面只用于提示客户，不能代替服务端付款确认。订单系统应把 PaymentIntent、Checkout Session、内部订单号和客户手机联系方式关联起来；Webhook 要验证签名、实现幂等并处理重复事件。

## 单次支付，不支持自动续费

MB WAY 属于 single-use 钱包支付。Stripe 当前产品文档不支持将 MB WAY 付款方式保存后用于 off-session 扣款、SetupIntent 或 setup_future_usage。因此，客户可以用 MB WAY 完成一次订单，但商家不能把这次付款直接视为已建立自动续费授权。

Stripe Billing 和 Invoicing 可能在 send_invoice 场景中提供 MB WAY 作为客户手动付款方式，但这和自动续费不同。订阅账单可通过发送付款说明让客户逐期手动完成支付；如果业务需要自动扣款，则应同时提供支持保存与重复扣款的方式，并在产品页明确说明。

MB WAY 不支持手动捕获或部分捕获。需要先授权、之后再确定最终金额的业务，应评估是否改用其他支付方式。不要在创建订单后依赖增量授权或多次 capture 来补足订单金额。

## 退款和退款状态

Stripe 当前文档列出 MB WAY 退款窗口为付款完成后 365 天。支持全额退款、部分退款和多次部分退款，但累计退款金额不能超过原始交易金额。退款返回到客户原始付款方式。

商家应在 Dashboard 或 Refunds API 提交退款，然后追踪 Refund 对象状态。Stripe 会通过 refund.updated 或 refund.failed webhook 通知最终结果。若退款失败，金额会返回 Stripe 余额，商家需要通过其他方式向客户退款。客服不要仅凭“已提交”就承诺款项已到账，应等 Stripe 最终状态并告知银行处理可能还有时间差。

对于部分退款，要在订单中保存原始总额、各次退款、剩余可退金额和退款原因。若一笔订单包含多件商品，应把商品行与退款金额对应，避免超过原始支付金额。

## 争议与证据时限

客户可以针对疑似欺诈、重复付款或订单金额与交易金额不符等原因发起 MB WAY 争议。Stripe 会暂扣争议金额，商家需要根据 Stripe 通知准备材料。当前 Stripe 文档列出提交证据的期限为 7 个日历日，时间较短，团队应设置自动告警和明确责任人。

证据可能包括物流跟踪号、发货日期、购买记录、数字商品的 IP 地址或邮件收据、客户手机号码、收货证明和退款记录。商家应在争议发生前就保留相关订单与履约记录，而不是收到邮件后才开始寻找材料。

如果商家赢得争议，被暂扣金额会返回 Stripe 余额；如果客户胜诉，对应扣款成为永久结果。争议事件应关联内部订单、客户、PaymentIntent 和 Dispute 对象，财务团队也要更新对账状态。

## Checkout 与其他 Stripe 产品支持

Stripe 当前列出 MB WAY 支持 Checkout 全页、Payment Links、嵌入式表单、Payment Element、In-app payments、Invoicing、Billing 和 Connect。它不支持 Express Checkout Element、Customer Portal、Terminal、SetupIntents 或 PaymentIntents 与 setup_future_usage。具体 UI 和 API 支持需要按当前集成确认。

对于多数商家，使用 Stripe Checkout 或 Payment Links 可以减少单独实现钱包认证的工作。若使用 Payment Element，需测试手机输入号码、应用授权、用户取消和返回页面。使用 Payment Links 时，确保订单备注、客户邮箱、产品金额和币种正确传入。

## 常见接入错误

**只检查商家 EUR 结算账户。** 客户国家为葡萄牙，需确认目标用户和账户资格。

**把客户日限额当成 Stripe 单笔限额。** 商家单笔最多 5,000 EUR，用户日累计限制则由 MB WAY 应用和客户设置影响。

**将 MB WAY 用于自动续费。** 它不支持 off-session 付款和保存授权；订阅可能需要 send_invoice 手动支付。

**手机号输入只允许 +351。** MB WAY 支持国际号码，输入组件应兼容国际格式。

**没有为 7 天争议时限设置告警。** 证据准备要提前保存，收到争议后快速提交。

**提交退款就立即关单。** 等待 Refund 对象最终状态，退款失败时另行处理。

## 上线清单

- Stripe 商家账户地区和 B2C 业务符合资格；
- 目标客户位于葡萄牙，价格使用 EUR；
- 订单金额在 0.50 至 5,000 EUR 范围；
- 客户手机号输入支持国际号码；
- MB WAY 单次支付与应用授权流程测试完成；
- 不在自动续费中依赖保存 MB WAY 付款方式；
- 付款成功由 Stripe 服务端状态确认；
- Refund 对象和 webhook 能处理全额、部分及失败退款；
- 争议告警确保不超过 7 个日历日提交期限；
- 保存物流、数字交付、手机号与客服沟通证据；
- Connect 场景确认账户上下文和资金对账。

## 总结

Stripe MB WAY 为葡萄牙消费者提供基于手机号和手机应用的单次支付体验。它使用 EUR，支持多国商家账户，但客户在葡萄牙且业务仅支持 B2C；商家单笔最高金额和客户在钱包应用中的每日累计限额需要分别考虑。

MB WAY 不支持保存后自动扣款、SetupIntent、手动捕获或部分捕获。全额与部分退款可在付款后 365 天内发起，争议举证窗口为 7 个日历日。使用服务端确认、退款状态同步和快速争议告警，才能把付款、客服和财务流程连起来。

## 参考资料

- [Stripe：MB WAY 支付方式说明](https://docs.stripe.com/payments/mb-way)
- [Stripe：MB WAY 接入指南](https://docs.stripe.com/payments/mb-way/accept-a-payment)
- [Stripe：Refund 对象 API](https://docs.stripe.com/api/refunds/object)
- [Stripe：Webhook 签名验证](https://docs.stripe.com/webhooks/verify)
