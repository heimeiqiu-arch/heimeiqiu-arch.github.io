---
title: "Stripe PayPay 接入指南：日本 JPY 支付、5 分钟授权与退款"
date: 2026-11-15
slug: "stripe-paypay-japan-jpy-authorization-expiry-refund-guide"
description: "介绍 Stripe PayPay 日本商家资格、JPY 金额范围、应用授权的双重过期时间、SCTA 网站要求、单次付款及退款处理。"
keywords:
  - Stripe PayPay
  - PayPay Stripe 接入
  - 日本 JPY 收款
  - PayPay 5 分钟授权
  - Stripe PayPay 退款
tags:
  - Stripe
  - PayPay
  - 日本支付
  - 数字钱包
---

PayPay 是日本常见的数字钱包和移动支付服务。客户使用 PayPay 应用认证并完成付款，Stripe 将结果通知商家。对于在日本经营的在线商家，PayPay 可以提供本地钱包付款方式，但启用前需要确认日本 Stripe 账户资格、网站展示要求和业务类别限制。

PayPay 的授权时效有两个容易混淆的期限：PayPay 应用授权在客户被重定向后 5 分钟过期；Stripe 支付尝试则在创建支付尝试 1 小时后过期，并会报告 payment_intent_payment_attempt_expired。把这两个时间与订单过期策略分开处理，可以避免用户还在结账页面时系统误判订单状态。

## 日本账户、JPY 和业务类型

Stripe 当前 PayPay 文档列出的商家账户和客户所在地均为日本，展示币种为 JPY，不支持跨境客户使用。账户类型支持单一 Merchant，不支持 Connect 平台或 Marketplace。业务模型可为 B2B 或 B2C，但仍需检查 Stripe 和 PayPay 的业务类别限制。

单笔金额范围为 50 JPY 至 1,000,000 JPY。创建 PaymentIntent 或 Checkout Session 时，后端应验证币种、金额和账户资格。不能仅因为客户浏览器使用日文或 IP 位于日本，就假设 PayPay 一定可用于当前商家账户。

PayPay 是单次使用支付方式，不支持保存后自动续费，也不支持手动捕获、部分捕获或后续金额调整。若商家的订单价格会在支付授权后变化，应在客户确认前确定最终价格，或提供适合需要后续捕获的其他支付方式。

## 网站审核和 SCTA 页面

Stripe 可能在启用后审查商家资格。当前文档要求商家网站展示的信息与 onboarding 提交资料相符，清楚说明销售的商品或服务、支付流程以及是否销售数字商品或服务，并提供完整的 SCTA（Specific Conditions of Transaction Acceptance）页面。

SCTA 页面应按照 Stripe 当前要求维护，并与网站的商家信息和实际交易流程一致。商家还要检查其 MCC 是否属于 PayPay 禁止或受限范围。若网站内容、商家名称或商品描述与开户资料不一致，支付能力可能受到限制；启用前应先完成网站资料和合规页面。

不要只因为 Stripe Dashboard 能打开支付方式设置，就认为 PayPay 已经通过生产审核。申请后要查看 capability 状态和 Stripe 通知，如有疑问向 Stripe 支持确认。

## 客户应用授权与双重过期时间

PayPay 付款会将客户带到 PayPay 应用进行认证。PayPay 端的授权窗口从客户重定向后开始计算，5 分钟后过期；Stripe 的支付尝试则有独立的 1 小时有效期。也就是说，PayPay 授权过期与 Stripe PaymentIntent 支付尝试过期不是同一件事。

订单系统应为用户显示清楚的待授权状态，并记录 PaymentIntent、支付尝试和 Checkout Session 的时间。客户未完成手机授权时，不应提前发货；若用户返回商家页面，要从服务端刷新支付状态，而不是假设付款失败或成功。

Stripe 文档列出 payment_intent_payment_attempt_expired 事件用于支付尝试过期场景。Webhook 处理需要验证签名并实现幂等。对于超时订单，应按当前 Stripe 对象状态决定是否让客户重试或创建新的支付尝试，避免重复收费。

## Checkout 与支付集成方式

多数商家可以先在 Stripe Dashboard 启用 PayPay，并使用 Checkout 或 Stripe 动态支付方式展示。若集成手动指定 payment_method_types，要确认 PayPay 包含在当前配置中。创建 Session 时使用可信的 Price、商品数量、JPY 币种和订单标识。

PaymentIntent 和 Checkout Session 都应在服务端创建，客户端不要自行决定最终金额。支付成功后，服务端通过 Stripe 对象状态和 webhook 更新内部订单。成功页面可以展示订单状态，但不要把浏览器跳转单独当成支付凭证。

## 退款处理和无争议流程

PayPay 支持全额和部分退款，退款需在原始付款后 365 天内提交。退款会即时完成，不能取消；资金会返回客户的原始付款来源，可能是 PayPay 余额或关联的支付方式。退款不是通过冲正原始交易来处理。

商家应在退款前核对订单、Refund 对象和累计已退金额。多次部分退款的总和不能超过原始交易。提交后要通过 Stripe Dashboard、Refund 对象和 refund.updated 或 refund.failed webhook 跟踪结果，失败时 Stripe 会把金额退回商家 Stripe 余额，商家需要通过其他方式退款。

Stripe 文档说明 PayPay 不支持标准争议或信用卡拒付流程，客户不能发起 chargeback，也不会因争议从 Stripe 余额扣款。这并不代表商家可以省略订单记录和客服机制；客户疑问仍需依据付款与履约记录处理。

## 常见接入错误

**将 PayPay 视为跨境钱包。** 当前客户使用范围为日本，展示币种为 JPY。

**把 PayPay 账户资格用于 Connect。** 目前 Stripe 文档列出 Merchant 支持，平台或 Marketplace 不支持。

**将 5 分钟与 1 小时过期混为一谈。** 一个是 PayPay 端授权期限，一个是 Stripe 支付尝试的过期时间。

**用 PayPay 做订阅自动扣款。** 该方式不支持 recurring payments 或保存后 off-session 扣款。

**假设可以手动捕获。** PayPay 不支持 manual capture，创建付款时应确定好最终金额。

**提交退款后允许客户继续使用未退款商品。** 退款应与订单、履约和访问权限规则一致。

## 上线检查清单

- Stripe 商家账户为日本账户并通过 PayPay 审核；
- 业务类别符合 PayPay MCC 规则；
- 网站展示商品、支付流程、数字商品说明和完整 SCTA 页面；
- Price 使用 JPY，金额在 50 至 1,000,000 JPY；
- 手机端 PayPay 授权流程经过测试；
- 5 分钟授权过期与 1 小时支付尝试过期分别处理；
- Webhook 事件签名校验和去重正常；
- 不把 PayPay 用于自动续费或手动捕获；
- 退款流程在 365 天窗口内可操作；
- 订单仅在服务端确认付款后履约。

## 总结

Stripe PayPay 为日本客户提供移动钱包授权体验，使用 JPY，单笔金额范围为 50 至 1,000,000 JPY。商家账户需要位于日本，且目前不支持 Connect 平台；网站还需要展示完整业务信息和 SCTA 页面。

PayPay 授权 5 分钟过期，Stripe 支付尝试则有独立的 1 小时过期机制。该方式是单次支付，不支持自动续费或手动捕获；退款可在 365 天内发起并即时完成。将两个过期时间、退款状态和订单履约纳入后台流程，可减少重复支付和错误状态。

## 参考资料

- [Stripe：PayPay 支付方式说明](https://docs.stripe.com/payments/paypay)
- [Stripe：PayPay Checkout 接入](https://docs.stripe.com/payments/paypay/accept-a-payment)
- [Stripe：PaymentIntent 过期事件](https://docs.stripe.com/api/events/types)
- [Stripe：退款对象 API](https://docs.stripe.com/api/refunds/object)
