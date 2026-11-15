---
title: "Stripe Affirm 分期支付：资格筛选、融资方案、退款和争议"
date: 2026-11-15
slug: "stripe-affirm-installments-eligibility-refund-dispute-merchant-guide"
description: "Stripe Affirm 如何在美国和加拿大提供分期付款，理解订单门槛、国内交易资格、商户预先收款、剩余分期退款和 15 天争议证据期限。"
keywords:
  - Stripe Affirm 分期支付
  - Affirm Stripe 退款
  - Stripe Affirm 资格
  - Affirm disputes Stripe
  - Affirm financing packages
tags:
  - Stripe
  - Affirm
  - 分期付款
---

Affirm 是先买后付（BNPL）支付方式，消费者在结账时登录或创建 Affirm 账户，选择可用的分期方案，再授权购买。商户通过 Stripe 接收款项，通常会先收到交易金额（扣除费用），Affirm 再向客户收取分期款。消费者看到的方案、期限和利率由 Affirm 根据交易、地区和资格决定，不是商户可以为每位客户保证的固定报价。

Stripe Affirm 还受严格的国家和交易类型限制，商户所在地和顾客所在地要处于同一国家；平台动态支付方式筛选可减少不合资格客户看到按钮。退款会取消客户尚未到期的计划分期，并返还已支付部分，但已支付利息可能不退。本文梳理商户资格、融资方案、订单履约、退款、争议和页面文案。可用国家、门槛和融资期限会变更，应以当前 Stripe Dashboard 和 Affirm 付款页面为准。

## 商户资格与国内交易要求

Stripe 文档当前将 Affirm 普遍开放给美国和加拿大账户；英国处于私有预览。顾客也需要位于美国或加拿大，且交易为本地交易：美国商户卖给美国客户、加拿大商户卖给加拿大客户。不要将 Affirm 当作跨境 BNPL 付款方式。

商家需为消费者业务（B2C），并符合 Stripe 与 Affirm 的行业限制。B2B 服务、预售、NFT、某些汽车和专业服务可能被禁止或需要额外审批。医疗服务虽然可能被允许，但需满足附加要求。完整业务清单和 MCC 限制应在申请前确认；网站还要公开可访问并显示客户当地币种的价格。

如果使用动态支付方式，Stripe 可根据客户国家筛选 Affirm。若自行设置 payment_method_types，则必须在服务端和前端确保只向符合国家、币种和金额条件的客户展示。错误展示给跨境客户，容易造成无法创建 PaymentIntent、结账失败或客户误以为可申请融资。

## 分期方案与订单门槛

Affirm 会按购物车金额、客户资格和 financing package 显示可用方式，例如短期分期或数月还款。Stripe 文档中的门槛和方案按国家、币种区分；具体期限和利率由 Affirm 决定并可能调整。商户不要在广告、价格页或客服中保证每位客户都能获得 0% APR、Pay in 4 或某个固定月供。

Stripe Dashboard 中可能配置 Standard 或 Enhanced financing package。方案可能影响客户看到的产品组合，但不能越权承诺客户资格。月供方案可能带利息，客户看到的总成本应按 Affirm 授权页为准。页面展示分期营销信息时，遵守 Affirm 的营销合规指南，并使用 Stripe 提供的 Payment Method Messaging Element 或批准的内容。

订单结账金额必须与服务端创建的 PaymentIntent 或 Checkout Session 一致。若优惠、税额、运费或用户选择的商品改变，重新计算最终金额，再发起支付。不要把分期月供金额作为商户订单应收金额；商户的 Stripe 账务通常记录完整订单总额，客户与 Affirm 之间的分期还款是另一组关系。

## 授权与商户收款

客户选择 Affirm 后会被重定向至 Affirm 网站或 App 登录、选择融资方案并授权。Stripe 文档当前说明授权成功后会确认支付，商户按 Stripe 支付结果继续履约。订单成功通知应说明商户已收到 Stripe 付款，并可向客户提示其还款计划由 Affirm 管理。

服务端仍要根据 PaymentIntent/Checkout Session 状态确认，而不是只凭浏览器返回。验证 Webhook 签名、保存 Event ID、核对订单号、金额、币种和 Customer，再幂等地创建发货单或开通权益。若高价值商品遇到 Stripe 或 Affirm 请求暂停发货的风险通知，应迅速核实并遵从对该交易给出的处理要求，避免在调查期间继续发货产生无法追回的损失。

Affirm 不支持 recurring merchant-initiated payments、off-session 或 SetupIntent 保存付款方式，也不适用于自动订阅扣款。消费者分期还款由 Affirm 收取，不等于商家获得可以对客户再次扣费的授权。

## 退款会影响消费者剩余分期

Stripe Affirm 退款通常需要在原付款后 120 天内发起，支持全额和部分退款，处理可能需要两天且为异步过程。退款提交后不能取消。退款状态通过 Refund 对象和 refund.updated 或 refund.failed Webhook 跟踪；只有看到最终状态后才能确认账务完成。

Affirm 收到退款后，会取消客户尚未支付的预定分期，并返还客户已经支付的金额。已经支付的利息可能不退。客户在 Affirm 账户中看到计划更新，具体最终余额由 Affirm 按其融资条款计算。客服在批准退货时应解释商户退款与消费者贷款计划更新之间有延迟，避免承诺“所有已付款金额和利息都会原样退回”。

如果 Refund 状态变为 failed，Stripe 会将相应金额返还 Stripe 余额，商家需要通过其他方式退款。按 PaymentIntent、Refund ID、客户融资账户后续变化和订单号关联记录，避免商户已经退给客户但 Stripe 退款仍在处理时重复支付。部分退款要累计校验，不超过原始订单金额。

## 争议与证据提交

Affirm 支付仍可能出现争议，客户通常有最长 120 个日历日提出；每个争议都是独立对象，可针对同一笔支付出现多次。Stripe 收到争议后会暂扣争议金额，向商家发送邮件、Dashboard 通知和 charge.dispute.created 事件。

商户通常有 15 个日历日提交证据，最终判定可能需要更长时间。以 Dispute 对象和 Dashboard 的具体截止日期为准，并保存订单履约证据：物流跟踪、发货日期、客户收货证明、数字商品访问日志、服务记录、退款记录和结账时展示的条款。胜诉时争议金额返还 Stripe 余额；败诉时扣款可能成为永久损失。

Affirm 客户已通过其账户授权，不代表商户免于争议，也不意味着无需响应 Stripe 或 Affirm 的暂停发货请求。建立争议队列并按 case deadline 提醒负责人，分别关联每个 Dispute ID 和支付订单。

## 对账与常见故障

Affirm 的交易按商户订单总额记录，而客户的分期账单由 Affirm 管理。财务对账关联 PaymentIntent、Charge、Refund、Balance Transaction 与 Stripe payout；不要把消费者后续每期还款当成商户的 Stripe 收款。

**Affirm 按钮不显示。** 检查商户与客户是否处于同一支持国家、币种和订单金额是否符合门槛、Dashboard 资格和动态支付方式筛选。

**客户没有看到预期分期方案。** 方案由 Affirm 根据金额、国家和消费者资格动态决定。不要在网站硬编码所有客户都能使用的方案；以授权页面最终选项为准。

**退款后客户仍看到分期账单。** 查询 Refund 最终状态并告知 Affirm 账户需要时间更新；已支付利息可能不退。

**平台想让卖家收 Affirm。** 确认 Stripe Connect 业务模式和 charge type 支持情况；并非所有平台账户模式都可以直接启用。

## 上线前验证清单

测试美国与加拿大本地交易、跨境客户被筛除、各金额段可用方案、Affirm 授权取消、付款成功、风险审核暂停、部分/全额退款、已付利息说明、退款失败、争议创建和 15 天证据截止提醒。确认融资价格广告遵循 Affirm 合规内容，客服不会保证利率和客户资格。

Affirm 将消费者融资决策与商户收款流程分开：商户通过 Stripe 收取交易款，客户按 Affirm 批准的方案还款。准确筛选本地交易、以 Stripe 事件驱动订单、让退款正确更新剩余分期，并在争议期限内提交证据，能减少结账拒绝和售后误解。

## 官方资料

- [Stripe：Affirm 支付](https://docs.stripe.com/payments/affirm)
- [Stripe：Affirm 退款和争议](https://docs.stripe.com/payments/affirm)
- [Stripe：Affirm 营销合规](https://docs.affirm.com/developers/docs/compliance_and_guidelines)
- [Stripe API：退款对象](https://docs.stripe.com/api/refunds/object)
- [Stripe API：Dispute 对象](https://docs.stripe.com/api/disputes/object)
