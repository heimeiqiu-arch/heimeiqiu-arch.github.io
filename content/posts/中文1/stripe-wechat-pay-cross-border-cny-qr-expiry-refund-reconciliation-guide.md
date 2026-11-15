---
title: "Stripe WeChat Pay 跨境收款：二维码有效期、CNY 币种与退款到账"
date: 2026-11-15
slug: "stripe-wechat-pay-cross-border-cny-qr-expiry-refund-reconciliation-guide"
description: "Stripe 微信支付如何面向中国消费者收款，核对商户国家和 CNY 币种、桌面二维码两小时有效期、180 天退款窗口与微信交易号对账。"
keywords:
  - Stripe WeChat Pay
  - Stripe 微信支付
  - Stripe 微信支付 CNY
  - Stripe 微信支付退款
  - wechat_pay transaction_id
tags:
  - Stripe
  - 微信支付
  - 跨境收款
---

Stripe WeChat Pay 允许符合条件的商户向使用微信支付的消费者收款。消费者在微信 App 中授权；桌面结账通常展示二维码，用户用手机扫描完成付款。该方式适用于面向消费者的购买，不支持 B2B 交易；客户付款后资金仍按 Stripe 商户账户的 payout 安排结算。二维码也有授权时限，退款处理方式则与银行卡退款不同。

本文说明 Stripe 微信支付的商户资格、可用币种、二维码过期、退款、Connect 展示和交易对账。地区资格和产品支持会更新，部分企业类型和 Connect 流程处于预览或需要额外审核。请以 Stripe Dashboard 与当前文档为准，不要把“客户能用微信支付”推断成“任何 Stripe 商户都能启用”。

## 账户资格与 CNY 展示

Stripe 文档列出一组支持微信支付的商户账户国家，消费者通常位于中国。支持的展示币种取决于商户账户所在国家；CNY 在文档列出的全部支持账户国家中可用，客户在微信支付页面看到人民币金额。其他展示币种则与商户账户地区对应。应用应按账户国家和货币配置选择付款金额，不能仅根据客户地区写死汇率或假设任意币种均可结算。

微信支付目前是 B2C 支付方式，不适用于 B2B。Stripe 与微信支付都有禁止或受限业务类别，商户还需要提供完整、可访问的网站，清楚展示产品或服务、价格和可用结账流程。Stripe 账户资料与网站信息应一致；仅有社交媒体主页可能不满足审核要求。若支付方式被限制，应根据 Stripe 通知补充资料并申请复核，恢复资格取决于审核结果。

最低金额由 Stripe 的结算币种和转换规则影响；文档示例中的某个币种限额不能当作所有国家的统一上限。创建付款前，按账户国家和当前币种最小/最大金额检查交易，并在 Dashboard 验证微信支付已启用。

## 桌面二维码和移动支付流程

桌面用户选择 WeChat Pay 后，Stripe 显示支付二维码，客户使用微信 App 扫描并授权。创建支付请求后，客户需要在两小时内完成桌面二维码授权；过期后必须重新开始付款，创建新的支付尝试。移动端体验可能直接打开微信或在受支持的原生集成中调用微信支付，再返回商家应用。

过期二维码不能通过刷新页面复用。内部订单保存每个 PaymentIntent 的 ID、创建时间和状态；客户超时后，先查询原 PaymentIntent 是否仍然等待授权或已经成功，再安全地创建新的尝试。多次提交要使用幂等保护，避免客户因页面响应慢而获得多张可支付二维码。

成功页用于展示体验，履约应由服务端的 PaymentIntent 最终状态驱动。Webhook 接收端验证签名、保存 Event ID、读取 PaymentIntent 与 latest Charge，并检查金额、币种、客户和订单关联。客户完成支付后不一定会按预期回到网站，因此不应只依赖浏览器跳转开通服务或发货。

## 退款状态和客户到账

Stripe 当前文档说明，WeChat Pay 支持全额和部分退款，可在原交易后 180 天内提交。退款异步处理：与原付款同一天提交的退款会立即处理；之后提交的退款按每日中午（UTC+8）批次处理。若客户最初使用关联银行卡付款，银行到账可能额外需要 2 至 5 天。退款提交后不可取消。

WeChat Pay 退款不是原付款的 reversal，而是由微信支付退回客户最初的资金来源，可能回到微信余额或关联支付方式。通知客户时说明退款会回到原支付来源，并给出提交日期、金额和状态；不要把退款申请提交时间当成客户实际到账时间。

每个 Refund 都要读取状态并监听 refund.updated 或 refund.failed。succeeded 后记录最终完成；failed 后 Stripe 将金额退回余额，商家需要通过其他方式退款。避免只在订单表中把付款标记为“已退款”并丢弃 Refund ID；保留原 PaymentIntent、退款 ID、金额、币种、Webhook 事件和客服沟通记录，财务才能核对净额。

## 微信展示名称与 Connect

微信支付订单描述可能包含结算商户名称、online 和单笔付款描述；商户设置的 statement_descriptor 会作为信息的一部分，但不能保证微信交易历史或客户关联银行卡账单完全按该字符串展示。若使用 Connect，charge type 会决定微信订单描述中的商户名称来自平台还是 connected account。平台应在测试环境核对客户端展示，并在售后页面说明账单上可能出现的平台或商户名称。

Connect 对不同 charge type 的支持并不完全相同。某些 direct charge、on_behalf_of 或 connected account capability 可能需要 Stripe 私人预览权限；平台账户可用 WeChat Pay 不代表所有连接账户都自动可用。上线前要检查 charge type、账户 capability、是否需要申请访问以及业务模型是否符合审核条件。

财务对账时读取 PaymentIntent 的 latest_charge，并获取 payment_method_details.wechat_pay.transaction_id。内部记录同时保存 Stripe PaymentIntent ID、Charge ID、微信交易号、订单号、金额、币种和账户上下文。微信交易号适合与微信侧交易信息或客户支持问题关联，不应替代 Stripe 对象 ID。

## 争议和订阅限制

微信支付要求客户通过微信 App 授权，Stripe 文档当前说明不支持标准卡组织争议流程。但这不代表商家无需处理未交付、退款请求和投诉。保存订单条款、发货证明和客户沟通，按内部售后政策处理客户问题。

一般的微信支付集成不支持自动续费、SetupIntent 保存和 off-session 后续扣款。Stripe 文档中提到的 recurring WeChat Pay 仍处于 private preview，需要单独申请早期访问，并且支持范围有限。不要把该预览功能写成已普遍开放的标准集成。Checkout 也不支持使用 WeChat Pay 的 subscription mode 或 setup mode；Invoice 仅支持 send_invoice。订阅产品应选择已启用的周期支付方式，或让客户按期主动支付适用发票。

## 常见问题排查

**结账没有微信支付。** 检查商户账户国家、付款客户、展示币种、B2C 业务类型、网站完整度、账户审核和 Dashboard 支付方式开关。

**二维码过期。** 桌面 QR 授权窗口为两小时。查询旧 PaymentIntent 状态后，为客户创建新的付款尝试，不要重复展示旧码。

**客户说付了，订单没更新。** 查询 Stripe PaymentIntent，核对 Webhook 接收与签名；若已成功，使用内部履约任务幂等重放，不能因客户刷新页面再次发货。

**退款已提交但客户没看到。** 查询 Refund 状态和提交时间。检查是否等待每日退款批次，或客户使用关联银行卡导致额外到账时间。

**微信账单显示商户名不同。** 核对 Connect charge type、平台/connected account 身份和描述字段。Stripe 支付描述不保证在所有微信或银行界面逐字呈现。

## 上线验证清单

测试桌面二维码、移动端跳转、两小时过期、重复付款尝试、付款成功 Webhook、退款当天提交、次日批次退款、关联银行卡到账延迟、Refund 失败和 Connect 商户名称。确认不同账户国家可用币种、B2C 限制和网站审核条件都已处理，并明确产品不承诺未开放的循环付款能力。

WeChat Pay 为中国消费者提供熟悉的支付体验，但其商户资格、二维码有效期、退款批次和 Connect 能力都有边界。用 PaymentIntent 和 Webhook 驱动订单，按 Refund 最终状态跟踪退款，并保存微信交易号与 Stripe 对象的关联，能让跨境收款和售后对账更清楚。

## 官方资料

- [Stripe：WeChat Pay 支付](https://docs.stripe.com/payments/wechat-pay)
- [Stripe：WeChat Pay 收款接入](https://docs.stripe.com/payments/wechat-pay/accept-a-payment)
- [Stripe API：退款对象](https://docs.stripe.com/api/refunds/object)
- [Stripe API：PaymentIntent 对象](https://docs.stripe.com/api/payment_intents/object)
- [Stripe：Connect Statement Descriptors](https://docs.stripe.com/connect/statement-descriptors)
