---
title: "Stripe OXXO 现金券支付：五天有效期、延迟确认与退款替代流程"
date: 2026-11-15
slug: "stripe-oxxo-cash-voucher-expiration-delayed-confirmation-no-refunds-guide"
description: "Stripe OXXO 如何创建墨西哥 MXN 现金支付凭证，处理五天过期、次工作日确认、收款后履约，以及该方式不支持 Stripe 原路退款时的替代退款流程。"
keywords:
  - Stripe OXXO
  - OXXO 现金券 Stripe
  - Stripe OXXO 退款
  - OXXO voucher expiration
  - payment_intent.requires_action OXXO
tags:
  - Stripe
  - 支付方式
  - 墨西哥
---

OXXO 是墨西哥常见的线下现金支付方式。客户在网上下单后获得带有交易参考号的付款凭证，再到 OXXO 便利店柜台以现金支付。和银行卡即时付款不同，生成付款凭证只代表客户可以去门店付款，并不表示商家已经收到钱。Stripe 通常会在下一个工作日收到实际现金付款确认；如果应用在凭证生成后就发货，就会承担客户最终没有付款的风险。

另一个重要限制是 Stripe OXXO 目前不支持全额或部分原路退款。若商家决定退还 OXXO 客户款项，需要单独建立替代退款流程，并对客户身份、收款方式、审计和重复退款进行控制。本文讲清凭证有效期、延迟状态、履约时机、退款限制和财务对账要点。产品可用范围会变化，请上线前核对 Stripe Dashboard 与最新文档。

## 付款凭证不是已付款订单

客户选择 OXXO 并提供姓名和邮箱后，会收到包含 32 位交易参考号的付款凭证。凭证会显示在 Stripe 托管页面，部分集成也可向客户发送付款说明链接。客户需要将凭证带到 OXXO 门店并以现金支付，收银员会给客户小票。只有门店完成现金收款，Stripe 后续才会确认 PaymentIntent 成功。

创建凭证时，PaymentIntent 会进入等待客户行动的状态，Stripe 会发送 payment_intent.requires_action，表示需要客户完成下一步；实际现金支付处理完成后，Stripe 会发送 payment_intent.succeeded。订单系统应把这两个阶段区分开，例如“等待线下付款”和“已付款”。凭证页面可用来提示客户支付，但在收到成功事件前不能把它等同于到账证明。

客户线下付款后，Stripe 通常在下一个工作日确认。周末、节假日和处理时间可能影响通知到达。对于数字服务，可根据产品风险决定是否提供临时受限访问；对于高价值或必须收到款项后才交付的商品，建议等服务端确认后履约。若采用临时访问，明确权限的截止时间和未付款时如何回收。

## 凭证过期与重复订单

OXXO 凭证默认五天后过期。PaymentIntent 的 payment_method_options[oxxo][expires_after_days] 可在支持范围内将期限设为 1 到 7 天。有效期应覆盖客户前往门店的时间，同时避免订单库存被长期占用。更改过期天数时，要同步调整购物车保留政策、库存锁定时间和客户邮件提醒。

凭证过期后，客户应返回网站重新开始支付流程，创建新的付款尝试并生成新凭证。不要把旧凭证链接包装成可无限重试的订单支付入口。内部记录应保存每次 PaymentIntent ID、生成时间、过期时间和状态，防止新旧凭证混淆。客户可能在旧凭证过期后才发现邮件，客服需要先查询旧订单是否仍有有效凭证，再决定是否生成新的支付尝试。

使用 Checkout Session 或 PaymentIntent 时，订单 ID 作为服务端关联信息保存。每次创建支付尝试都应有幂等策略；但幂等键不能导致已经过期的凭证被错误复用。对同一订单的新尝试，要确认旧尝试未支付、已过期或已取消，避免两张有效凭证同时对应同一订单。

## Webhook 决定履约时机

OXXO 的现金支付确认存在延迟，浏览器返回页面与 Stripe 收到门店付款确认不是一回事。履约应由服务端接收到 payment_intent.succeeded 并完成内部校验后触发。校验 PaymentIntent 金额、MXN 币种、内部订单号、客户信息和当前订单状态；Webhook 签名验证通过后保存 Event ID 并幂等处理。

payment_intent.requires_action 适合更新订单为等待付款并发送凭证说明，不应触发发货。支付成功事件可能延迟，用户也可能关闭浏览器，所以不要依赖前端回调。重复 Webhook 只能更新相同订单状态，不能重复扣减库存、发出多个数字兑换码或重复发送已付款通知。

如果客户提供 OXXO 小票截图而 Stripe 仍显示待付款，不要直接在内部把订单设为成功。先按 PaymentIntent 和参考号核实 Stripe 事件或支持记录，等待系统确认。小票能证明客户在门店尝试付款，但不能代替 Stripe 的最终支付状态，尤其是交易参考号输错、付款被拒或处理未完成时。

## Stripe 原路退款不支持时怎么办

Stripe 当前 OXXO 文档说明，OXXO 付款不能通过 Stripe Refunds API 原路退回，也不支持部分或全额退款。若业务政策要求退款，商家必须建立独立流程，例如经人工审核后通过支持的银行转账或其他付款方式退还客户。不要在产品页面承诺“点击退款即可原路退回 OXXO”，也不要因为 Dashboard 中看不到退款按钮就尝试重复调用接口。

替代退款流程需要充分核验收款人身份和原始订单关系。只向客户收集完成退款所必需的信息，提供安全提交渠道，并限制谁能查看和处理银行信息。记录原付款 PaymentIntent、订单号、客户核验方式、退款金额、替代付款凭证、审核人和完成日期。银行账号、收款姓名和原订单信息要按企业隐私与留存规则管理，不要把敏感资料写入普通日志或客服备注。

如果因为客户取消、缺货或重复下单需要退钱，先确认 Stripe 已确认这笔 OXXO 现金付款并核对是否已进入余额，再启动替代退款。若 Stripe 尚未确认付款，不要向未收到账的订单付款；若同一笔订单可能有多个现金凭证，逐一核对其最终状态，避免遗漏重复支付或向错误客户退款。

## 适用范围、币种和金额

Stripe OXXO 的客户使用地区为墨西哥，展示币种为 MXN，最低金额 10 MXN，最高金额 10,000 MXN。Stripe 账户资格当前涵盖若干国家，部分地区仍可能处于 private preview；支付方式还会受到账户审核和商户类别限制。支付方式是否能启用，应以账户 Dashboard 和 API 配置为准，不要根据另一家公司的接入情况推断自己的账户也具备权限。

OXXO 不支持 recurring、SetupIntent 保存付款方式、标准争议流程、Stripe 原路退款、手动捕获和部分捕获。Stripe Connect 支持相关流程，但平台还要检查 merchant of record 和 connected account 资格。OXXO 托管凭证页面显示交易参考号及承担销售责任的商户名称；Connect charge type 会影响客户看到的平台或连接商户身份。

## 对账与客服查询

在内部订单中保存 Checkout Session ID、PaymentIntent ID、OXXO 交易参考号、MXN 金额、凭证签发时间、到期时间、付款确认时间及相关 Balance Transaction。Stripe payout 与 OXXO 付款确认是两个阶段：先确认支付，再按 Stripe 账户的 payout 排程查看余额何时打到银行。不要把客户现金付款后的下一工作日确认误认为同日银行到账。

客户询问“我已经去门店付款，为什么订单还没完成”时，客服按参考号、订单号和 PaymentIntent 查询。向客户说明线下现金支付需要一定时间回传状态；若处理超过预期时间，记录门店小票信息并由财务核实。客户询问如何退款时，提前说明 Stripe 不支持 OXXO 原路退款，按照企业的替代退款流程办理，而不是误导其等待一个不存在的 Stripe Refund 状态。

## 常见问题排查

**客户拿到凭证但订单已发货。** 检查履约逻辑是否在 payment_intent.requires_action 或 Session 创建时触发。改为等待 Stripe 的成功付款事件。

**客户已在门店支付但 Stripe 仍未更新。** 核对付款参考号、金额和支付时间，查看 Stripe Webhook 投递与 PaymentIntent 最新状态，并考虑工作日处理延迟。不要依赖截图直接改账。

**凭证过期后客户再次下单。** 检查旧 PaymentIntent 最终状态，再创建新的支付尝试并保存新旧关系，避免两张凭证同时可用。

**客户要求退回 OXXO 现金付款。** Stripe 原路退款不支持。按企业替代退款政策核验客户和订单，记录替代付款凭证与审核流程。

**财务账上有凭证但没有收款。** 凭证签发是待付款，不是现金入账。只对 payment_intent.succeeded 的付款记为已收款，再将 Balance Transaction 与 payout 另行核对。

## 上线前检查清单

在测试环境验证凭证创建、默认五天过期、可配置有效期、客户未付款、现金支付后延迟确认、Webhook 重复投递、旧凭证过期后重新支付、重复付款和替代退款审批。确认客户邮件说明了门店现金支付步骤和最终确认时间，订单在未收到支付成功事件前不会误发货；财务可以按参考号匹配 PaymentIntent，并区分 Stripe 原路退款不支持与内部替代退款。

OXXO 能帮助没有银行卡或更愿意线下付现金的客户在线下单，但它改变了订单回传和退款设计。将凭证视为待付款、等待 Stripe 确认后履约，并提前规划不可原路退款时的客户处理方式，才能避免现金券订单变成客服和财务的盲区。

## 官方资料

- [Stripe：OXXO 支付](https://docs.stripe.com/payments/oxxo)
- [Stripe：OXXO 收款接入](https://docs.stripe.com/payments/oxxo/accept-a-payment)
- [Stripe API：创建 PaymentIntent](https://docs.stripe.com/api/payment_intents/create)
- [Stripe：Checkout 履约](https://docs.stripe.com/checkout/fulfillment)
- [Stripe：Webhook 签名验证](https://docs.stripe.com/webhooks/signature)
