---
title: "Stripe MobilePay 接入指南：丹麦与芬兰钱包、币种、退款和争议"
date: 2026-11-15
slug: "stripe-mobilepay-denmark-finland-wallet-payment-guide"
description: "介绍 Stripe MobilePay 的商家资格、丹麦与芬兰客户、DKK/EUR/NOK/SEK 币种、一次性支付、银行卡退款及 Connect 能力。"
keywords:
  - Stripe MobilePay
  - MobilePay Stripe 接入
  - 丹麦 芬兰 移动支付
  - MobilePay 退款和争议
  - MobilePay Connect
tags:
  - MobilePay
  - 丹麦支付
  - 芬兰支付
---

MobilePay 是丹麦和芬兰客户常用的手机钱包。Stripe 的 MobilePay 付款以客户在应用中确认的银行卡交易为基础，不是余额储值，也不是银行转账。客户在结账页面选择 MobilePay 后，跳转到手机应用或网页流程，确认要使用的卡片并授权付款。

接入时不能把“客户离开 Checkout”当作付款成功。应由 Stripe Session、PaymentIntent 和 Webhook 共同确认最终状态。MobilePay 支持一次性付款、手动捕获和部分捕获，也支持全额和部分退款；不支持 recurring payment、off-session 扣款、SetupIntent 或 Stripe Billing。商家在上线前要确认业务需要的支付流程与这些能力相符。

## 商家资格、客户地区和币种

Stripe 当前文档列出的商家账户资格覆盖多个 EMEA 国家，包括丹麦、芬兰及其他欧洲国家；客户使用 MobilePay 的所在地为丹麦和芬兰。也就是说，符合资格的欧洲商家可能接受丹麦或芬兰客户的 MobilePay 付款，但不代表所有国家客户都能选择此钱包。

可用展示币种为 DKK、EUR、NOK 和 SEK。具体可用性还要看商家账户、支付方式设置和结算账户。最低付款金额与商家结算币种有关；Stripe 的文档以结算为 DKK 时至少 2.50 DKK 为例，若发生币种转换，转换后的金额也必须满足结算币种最低要求。不要在前端仅按用户 IP 显示 MobilePay 按钮，而应由 Stripe 的动态支付方式或服务端资格判断决定是否展示。

Stripe 文档列出了 MobilePay 对部分业务类别和商户类别代码的限制。包括债券、债务催收、多层次营销等特定类型；某些 MCC 禁止使用，受限 MCC 可能要求商家在开户时提交额外材料。启用前查看 Stripe 当前受限行业清单和 MobilePay 支付方式页面，不要只凭行业名称自行判断。

## 客户付款流程和集成方式

多数商家可以通过 Stripe Dashboard 启用 MobilePay，再使用 Checkout、Payment Links 或 Payment Element。Stripe 文档将 Checkout 列为推荐集成之一。若自行列出 payment_method_types，要确认代码和账户设置已支持 mobilepay；若使用动态支付方式，Stripe 可根据客户所在地、币种和支付流程展示可用选项。

客户在桌面浏览器付款时，会继续到 MobilePay 页面并输入与账户关联的手机号，然后在应用通知中批准交易；手机端则可以转到 MobilePay 应用，检查金额、选择银行卡并确认。某些发卡行可能额外要求银行卡认证，MobilePay 应用会提供相应 WebView。Stripe 表示，底层 3DS 挑战对商家集成是不可见的，不需要另写认证处理逻辑，但商家仍应根据 PaymentIntent 和事件判断支付结果。

PaymentIntent 应由服务端创建，使用可信的 Price、数量和订单 ID。客户端返回的 Session ID 可用于查询状态，但不能直接作为发货凭证。服务端根据 webhook 或 Stripe API 核实状态，再更新订单和履约流程。

## 一次性付款与捕获限制

MobilePay 是单次使用方式，不支持周期性扣款或 off-session 复用。因此不能把它设置成订阅续费方式，也不能在客户不在线时自动扣款。产品若同时提供订阅和单次购买，需要在结账页面把 MobilePay 仅呈现给支持的单次购买流程。

MobilePay 支持手动捕获和部分捕获。部分捕获是最终捕获，Stripe 会释放尚未捕获的余额，之后不能对同一笔授权再次发起第二次捕获。对于可能变更金额的订单，例如酒店押金或按最终重量结算的商品，设计订单时要确认一次部分捕获是否足够；若需多次捕获，应选择支持多次捕获的支付方式。

此钱包不支持扩展授权、增量授权、重新授权、多重捕获或超额捕获。商家应在客户授权前确定订单总额，或明确选择更适合后续调整的付款方式。需要延后确认订单的场景，也要先验证 Stripe Session 和 PaymentIntent 的当前状态，以及库存和订单撤销规则。

## 退款和对账

Stripe 文档没有为 MobilePay 指定单独的固定退款截止日期，具体取决于银行卡网络和地区规则。商家可以通过 Dashboard 或 Refunds API 申请全额或部分退款，多次部分退款的累计金额不得超过原始付款金额。资金通常在 5 至 10 个工作日显示，实际时间取决于发卡行。

MobilePay 退款通过客户原始付款的卡片处理。付款后不久提交的退款有时会以冲正形式出现，即原扣款在账单上消失，而不是出现一笔单独入账。客服应向客户解释不同银行账单的显示方式，避免客户误以为退款没有处理。

在后台保存退款 ID、订单 ID、原始 PaymentIntent、退款金额和当前状态。监听 refund.updated 和 refund.failed，并验证 Webhook 签名。若退款失败，检查失败原因，再通过其他方式安排退款。不要只通过浏览器提示客户“已退款”，应根据 Refund 对象的状态更新订单。

## 争议、3DS 与 Connect

MobilePay 底层通过 Visa 或 Mastercard 卡交易处理，客户可以向发卡行提出卡片争议；不存在一套独立于银行卡争议的 MobilePay 专用流程。Stripe 会通过邮件、Dashboard 和 charge.dispute.created 事件通知商家，争议原因和回复期限可在 Dashboard 或 Dispute 对象的 evidence_details.due_by 中查看。商家应走标准卡争议流程提交证据并记录处理结果。

3DS 责任转移仅在交易实际发生 3DS 身份验证时适用。商家不能强制底层银行卡交易必须进行 3DS。不要把 MobilePay 的应用批准步骤当成一定完成了 3DS，也不要据此认为所有欺诈争议都会自动转移责任。

MobilePay 支持 Connect 商家和平台，但不能因此推断所有 Connect 付款模式都自动可用。需要在 connected account 上确认 mobilepay_payments capability 是否 active；没有完整 Stripe Dashboard 权限的账户可能需要平台通过 Capabilities API 申请该 capability。商家还要按 direct charge、destination charge 等实际资金流核对 webhook 上下文、退款责任和争议处理角色。

## 费用与账户展示

MobilePay 的交易基于银行卡处理，相关费用按照 Stripe 账户定价和适用规则收取。Stripe 文档说明某些 MobilePay 附加费用会单独汇总计费，丹麦的特定商家可能还有月度会员费。不同国家和协议的费用可能不同，因此应在 Stripe Dashboard 和当前 Pricing 页面核对，不能把网络搜索中某个地区的费率直接当成所有商家的报价。

消费者在 MobilePay 应用中看到的商家图标来自 Stripe Branding 设置。上线前上传正确的商家图标和公开名称，测试桌面网页跳转、移动应用跳转、付款取消后回到商家页面等路径。若未设置图标，应用可能显示默认图标，影响客户辨识交易来源。

## 常见接入错误

**把 MobilePay 当成订阅方式。** 它是单次支付，不支持 recurring、off-session 或 Billing。

**客户返回网页就发货。** 返回商家页面本身不证明付款成功，必须检查 Stripe 状态。

**将部分捕获理解成可分多次扣款。** 部分捕获是最终操作，未捕获余额会释放，不能再做第二次捕获。

**认为所有争议都由 MobilePay 独立处理。** 付款按底层卡网络交易处理，争议使用 Stripe 标准卡争议流程。

**把应用批准等同于 3DS 责任转移。** 只有实际发生 3DS 验证时才适用相应责任转移。

**按所在国家设置一套统一币种。** 可用币种和最低金额还受账户结算币种及支付资格影响。

**Connect 账户默认已启用。** 必须检查关联账户的 mobilepay_payments capability 状态。

## 上线前检查清单

- 商家账户国家及 MCC 符合 MobilePay 资格；
- 目标客户位于丹麦或芬兰；
- 支付页面按账户条件显示 DKK、EUR、NOK 或 SEK；
- Stripe Dashboard 中已启用 MobilePay；
- 测试手机应用与桌面端跳转、认证和返回流程；
- 仅在一次性订单展示 MobilePay，不用于订阅续费；
- 若用手动或部分捕获，确认单次捕获规则满足业务；
- Webhook 能识别付款成功、失败、退款及争议事件；
- 退款失败时有人工替代退款流程；
- Connect 账户的 capability 状态和资金流已验证；
- 品牌图标、客服信息和账单描述清楚可识别。

## 总结

Stripe MobilePay 为丹麦和芬兰客户提供手机应用确认的卡钱包体验，支持 DKK、EUR、NOK 和 SEK。它适合一次性结账，支持手动或部分捕获、全额或部分退款，并按 Visa 或 Mastercard 的底层交易处理争议。它不支持订阅、off-session 复用或 Stripe Billing。

上线前应检查账户资格、客户地区、币种、商户类别限制和 Connect capability。以服务端确认 PaymentIntent 和 Session 状态后再履约，保存退款与争议记录，并向客户清楚说明银行卡退款的到账时间和应用支付流程。

## 参考资料

- [Stripe：MobilePay 支付方式说明](https://docs.stripe.com/payments/mobilepay)
- [Stripe：MobilePay 收款接入](https://docs.stripe.com/payments/mobilepay/accept-a-payment)
- [Stripe：银行卡争议处理](https://docs.stripe.com/disputes/responding)
- [Stripe API：Refund 对象](https://docs.stripe.com/api/refunds/object)
