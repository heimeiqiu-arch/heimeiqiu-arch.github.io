---
title: "Stripe Wero 接入指南：欧洲银行转账、EUR、QR 确认与退款"
date: 2026-11-15
slug: "stripe-wero-europe-eur-bank-payment-guide"
description: "介绍 Stripe Wero 付款的欧洲账户资格、EUR 结算、二维码银行授权、Checkout 模式限制、730 天退款和无争议特性。"
keywords:
  - Stripe Wero
  - Wero Stripe 接入
  - 欧洲银行支付 EUR
  - Wero Checkout 退款
  - Wero QR Code 付款
tags:
  - Stripe
  - Wero
  - 欧洲支付
  - 银行转账
---

Wero 是一个基于银行账户的欧洲付款方式。客户通过 Wero 钱包或参与的银行应用确认交易，商家收到即时付款结果。与银行卡不同，Wero 属于客户主动授权的银行转账类支付，展示币种为 EUR。Stripe 当前将 Wero 标示为预览功能，因此启用资格和客户地区可能因账户及上线阶段而变化，上线前应以 Stripe Dashboard 与当前官方文档为准。

Wero 适合欧洲市场的一次性订单。它支持 Checkout、Payment Links、Payment Element 和 Connect，但不支持 recurring payments，也不能在 Checkout subscription 或 setup 模式使用。商家需要理解二维码跳转、银行限额、退款期限和不支持争议等差异，不能把用户从 Wero 页面返回网站当成付款成功凭证。

## 账户国家、客户地区与 EUR

Stripe 文档列出的 Wero 客户所在地包括比利时、法国、德国、卢森堡和荷兰，展示币种为 EUR。商家账户可用国家范围更广，包含部分 EEA 国家，例如奥地利、丹麦、西班牙、芬兰、法国、德国、荷兰、葡萄牙、瑞典等。账户地点与客户可使用地区不是同一个清单，商家不能仅因自己的账户在欧洲，就假设所有欧洲客户都能通过 Wero 付款。

Wero 最低付款金额为 0.50 EUR，最高金额通常取决于客户银行的限额。支付可能因银行的每日或单笔限额而失败，商家应提供卡片或其他银行支付方式作为备选。适用的行业和业务类别也有限制，例如成人内容、NFT、点对点汇款、武器、众筹等类别可能被禁止或限制。应在正式启用前检查 Stripe 对 Wero 以及 Stripe 通用受限业务的最新说明。

由于该方式目前处于预览阶段，账户资格、产品展示情况和地区可用性可能调整。不要在网站上写死“所有欧洲客户都能使用 Wero”，应将支付方式是否出现交给 Stripe 根据当前账户、币种和客户位置动态决定。

## 客户授权与支付状态

客户在 Stripe Checkout 选择 Wero 后，会被重定向到 Wero 授权页面。客户扫描二维码，打开手机上的 Wero 或银行应用并批准付款。Stripe 文档说明该支付通常即时处理，常见完成时间低于 10 秒，之后客户返回商家页面。

网页返回不是支付凭证。用户可能关闭页面、网络中断或被浏览器阻止跳转，但支付仍可能已成功；也可能用户返回时支付尚未完成。订单应通过 checkout.session.completed、PaymentIntent 状态或适用的 Webhook 在服务器端确认。验证 Stripe 签名并按事件 ID 去重，防止重复发货或重复开通数字商品。

创建 Checkout Session 时，服务端应从内部订单读取商品、数量、EUR 金额和订单标识。Wero 是一次性付款方式；如果使用手动列出 payment_method_types，要确认 Stripe 当前 Wero 的 API 值和 Checkout 集成要求。使用动态支付方式时，在 Dashboard 启用 Wero，由 Stripe 判断哪些客户和订单符合条件。

## 产品能力和集成模式

Wero 支持 Checkout、Payment Links、Elements 和 Connect。Stripe 文档提示 Checkout 的 subscription 和 setup 模式不支持 Wero，Express Checkout Element 也不支持。商家可以通过 Dashboard 启用它，并在 Payment Element 或 Stripe Checkout 中呈现；若手动管理支付方式列表，按 Stripe 的 Wero 接入说明逐项配置。

Wero 支持手动捕获及全额、部分退款，但不支持周期性付款。对于普通电商订单，通常选择一次性 payment 流程。如果订单需要按月扣款、保存银行账户以后再次使用或执行 off-session 收费，就必须采用另一种 Stripe 支付方式。不要通过创建后续 PaymentIntent 模拟自动续费，因为 Wero 不提供复用授权。

Connect 平台可以支持 Wero，但平台仍需检查其账户国家、连接账户能力、交易币种及付款责任。上线前确认平台自己的资金流模式和 Stripe 的当前预览状态，避免在少数账户可见时就默认所有卖家都能收款。

## 退款期限与对账

Wero 支持全额与部分退款，并允许多笔部分退款，只要累计金额不超过原始付款金额。Stripe 文档列出的提交窗口最长为原始付款后 730 天。退款期限是支付方式允许的最晚时间，并不会自动决定商家的退货政策；退货和退款条件还要符合销售条款与当地规定。

创建退款后，应读取 Refund 对象状态并通过 refund.updated 或 refund.failed Webhook 跟踪最终结果。不要在退款请求提交后立刻将订单状态标记为“退款成功”。如果退款失败，检查 Stripe 提供的失败原因，并按客服政策通过其他方式退款。内部系统应保存订单 ID、Checkout Session、PaymentIntent、Refund ID、原支付金额、累计退款金额及退款状态，便于财务核对。

Wero 付款来自银行账户转账，商家对账时要区分客户授权、Stripe 付款状态、余额交易和后续 Payout。账单显示内容可能由客户银行决定；提供支付确认页时，显示 Stripe 服务端确认的订单金额、币种与时间，不从 URL 参数或前端状态中推算。

## 不支持争议意味着什么

Stripe 当前文档显示 Wero 不支持争议流程。客户不能通过 Stripe 的标准银行卡争议机制提交 chargeback，并不代表商家无需处理客服纠纷，也不代表交易绝不会发生退款、撤回或银行侧问题。商家仍要保留客户授权、商品交付、沟通和退款记录，并通过适当的客户服务流程处理争议。

与银行卡不同，Wero 付款由客户通过银行或钱包应用主动授权。页面上应清楚展示金额、币种、商户名称和订单内容，避免客户误授权。大额或高风险订单可在确认到账后才发货；但具体风险控制还需要按照业务、Stripe 规则和银行流程评估。

## 常见错误

**把 Wero 当成欧元银行卡。** 它是经银行或钱包认证的账户转账方式，有不同的退款和争议特征。

**认为所有 EEA 客户都能使用。** 商家账户可用国家和客户位置范围不同，且预览期间资格可能变化。

**订单页面返回就立即交付。** 必须从服务端核实支付状态，并通过 Webhook 兜底。

**用 Wero 做订阅续费或离线扣款。** 它不支持 recurring、off-session 及 Checkout subscription/setup 模式。

**认为部分退款可以无限次。** 多笔退款总额不能超过原始付款金额，且必须留在允许的退款提交窗口内。

**忽略银行金额限额。** 大额交易可能受客户银行限额影响，应提供备选付款方式。

**以为不支持争议就没有售后工作。** 仍需处理退款请求、客户投诉及交付证明。

## 上线前检查清单

- Stripe Dashboard 中账户已获得 Wero 使用资格；
- 客户位置属于当前支持范围，展示币种为 EUR；
- 最低金额不低于 0.50 EUR，并考虑客户银行上限；
- 受限行业与 MCC 规则已经核对；
- 只在一次性 Checkout 流程启用，不用于订阅或 Setup；
- 测试二维码、手机银行授权、取消和返回流程；
- 用服务器端 PaymentIntent 或 Checkout Session 状态确认付款；
- Webhook 验证签名、去重并能安全重试；
- 退款在 730 天窗口内按商家退款政策提交；
- 部分退款累计不超过原始付款金额；
- 为无法使用 Wero 的客户提供替代支付方式；
- 保存 Stripe 事件和订单对账记录。

## 总结

Stripe Wero 为部分欧洲地区客户提供 EUR 银行账户支付体验：客户在 Wero 或参与银行应用中扫描二维码并主动确认，支付通常实时完成。它适合一次性线上订单，支持 Stripe Checkout、Payment Links、Elements、Connect 及部分退款，但不支持订阅和 off-session 付款。

启用前要核对预览资格、商家国家与客户地区差异、银行金额限制和受限业务。使用 Webhook 与服务端状态确认付款，退款按 Stripe 规定的 730 天窗口跟踪，并注意该方式不支持标准争议流程。

## 参考资料

- [Stripe：Wero 支付方式说明](https://docs.stripe.com/payments/wero)
- [Stripe：Wero Checkout 接入](https://docs.stripe.com/payments/wero/accept-a-payment)
- [Stripe API：Refund 对象](https://docs.stripe.com/api/refunds/object)
- [Stripe：Checkout 履约指南](https://docs.stripe.com/checkout/fulfillment)
