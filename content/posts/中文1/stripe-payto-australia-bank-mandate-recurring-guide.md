---
title: "Stripe PayTo 接入指南：澳大利亚银行授权、Mandate 与扣款"
date: 2026-11-15
slug: "stripe-payto-australia-bank-mandate-recurring-guide"
description: "详解 Stripe PayTo 的澳大利亚账户与 AUD 要求、PayID 或 BSB 授权方式、Mandate 参数、交易限额、退款和不可申诉的争议处理。"
keywords:
  - Stripe PayTo
  - PayTo Stripe 接入
  - 澳大利亚 AUD 支付
  - PayTo mandate
  - Stripe PayTo 订阅扣款
tags:
  - Stripe
  - PayTo
  - 澳大利亚支付
  - 银行扣款
---

PayTo 是澳大利亚的实时银行支付方式，可用于一次性付款和经常性付款。客户可以提供 PayID，或输入银行 BSB 与账户号码；银行通常会通过推送通知或邮件发送授权请求，客户在手机银行或网银中批准 Mandate。授权后，商家可根据 Mandate 条款发起符合范围的付款。

PayTo 与银行卡自动扣款的产品体验不同：客户需要在银行渠道明确授权，支付确认可能延迟，授权金额、频率、用途和有效期由 Mandate 约束。Stripe 还要求启用 PayTo 前完成额外身份验证。本文说明接入资格、金额限制、授权设计、重复扣款、退款和争议流程。

## 商家与客户资格

Stripe 当前文档列出 PayTo 商家账户和客户所在地均为澳大利亚，展示币种为 AUD，地理覆盖为国内交易。商家业务模型可为 B2B 或 B2C，Merchant 和 Connect 平台/Marketplace 账户均列为支持，但账户仍可能接受额外资格审查，且业务类别有禁止或受限清单。

启用 PayTo 前，商家需要在 Dashboard 支付方式设置中请求访问，并按照 Stripe 提示完成额外身份验证。不要在只看到支付方式设置入口时就认为生产能力已完全开放；确认账户审核状态、MCC 和当前支付能力后，再安排正式上线。

## PayID 与 BSB 账户授权

PayTo 支持两类客户输入：

- **PayID**：与银行账户关联的唯一标识；
- **BSB 与账户号码**：澳大利亚银行账户编号和分行代码。

两种方式都会触发客户银行发送授权请求，通常通过银行应用通知或邮件。用户必须在银行应用或网银中确认 Mandate。网站应清楚说明客户下一步会收到银行授权请求，并提供订单查询入口，避免客户停留在待授权状态时误以为交易失败。

一次性付款的 Mandate 由 Stripe 自动设置，商家不必自行填写 Mandate 条款。订阅或其他重复付款必须明确配置 Mandate 选项，规定金额、金额类型、频率、用途和允许期限。Stripe 建议仅请求完成收款所必需的最小权限，并设置合理金额上限；部分银行可能拒绝没有指定金额的 Mandate。

## 经常性扣款 Mandate 的设计

Mandate 描述客户授权商家如何扣款，包括金额、周期、用途和允许的时间范围。金额可以采用固定金额，也可以设置最高金额约束；频率可以按约定周期，也可能使用按需扣款模式。产品和银行对 Mandate 字段有具体限制，必须结合当前 API 文档和订阅业务确认。

设计时应让 Mandate 与客户看到的订阅条款一致。若客户授权每月最多扣取某金额，商家不能在后台将扣款改成超过其授权的金额。升级套餐、改变扣款周期或调整金额时，先判断现有 Mandate 是否覆盖新条款；不覆盖时，应重新取得客户授权，而不是只修改订阅 Price。

客户可以通过银行应用或联系银行撤销 Mandate；商家也可通过解绑相关 PaymentMethod 取消 Mandate。平台应将授权状态与 Stripe PaymentMethod、Customer 和 Subscription 关联，客户撤销授权后停止未来扣款，并引导客户选择新的付款方式。

## 延迟确认与订单状态

Stripe 将 PayTo 的付款确认时机列为 Delayed。订单应有“等待银行授权”“授权处理中”“付款成功”“付款失败或取消”等状态。客户提交支付后，平台不能立即将订单标为已付；应等待 Stripe 服务端状态或 webhook 确认后再履约。

对订阅来说，Mandate 创建成功和每次扣款成功是两回事。每笔 off-session 付款都需要依据 Stripe 返回的 PaymentIntent、Invoice 和 Subscription 状态处理。付款失败时，系统应通知客户并采用业务定义的重试或更新授权方式，不要无限重复提交扣款。

Webhook 要验证签名、实现幂等，并记录客户、账户、PaymentIntent、发票和 Mandate ID。由于事件可能延迟或重试，后台要读取当前对象状态后再执行权益变化，避免重复开通或错误暂停服务。

## 单笔金额限制

Stripe 当前文档列出的 PayTo 单笔最低金额为 0.50 AUD，技术支持的最高金额为 100,000 AUD。但这个最高值不等于所有账户默认都可以处理这么大金额：默认账户单笔上限为 10,000 AUD，经过批准后才可能处理最高 100,000 AUD。客户银行对 Mandate 和单笔扣款也可能施加自己的限制。

在创建 PaymentIntent 或订阅 Mandate 前，服务端应同时校验 Stripe 账户处理上限、Mandate 授权金额和银行可能的限制。若业务要处理高金额付款，应在投产前联系 Stripe 确认账户已获批，而不是在用户付款失败后再排查限额。

## 退款与 PayID 姓名匹配

PayTo 支持全额和部分退款，累计退款不能超过原始付款。Stripe 文档当前列出退款可在原付款后最长 2 年内提交；客户通常几分钟可在银行账户看到退款，但部分银行可能需要数天。

若原支付通过 PayID 完成退款，payment_method.billing_details.name 需要与客户银行账户姓名一致，不匹配可能导致退款失败。商家应在支持团队排查流程中保留付款方式、姓名字段和退款对象关联信息，并在提交前核对 Stripe 返回的数据。退款提交后应持续跟踪 Refund 状态，不应仅凭 API 请求成功就宣称银行已入账。

## 争议不可申诉

Stripe 文档说明，PayTo 争议发生后会从 Stripe 余额扣除争议金额及相关争议费用。PayTo 争议为最终结果，商家无法提交证据来挑战或申诉。Stripe 会通过 charge.dispute.created 与 charge.dispute.closed webhook 通知争议状态。

如果客户与商家协商解决并同意返还资金，客户需要重新付款，而不是通过恢复原争议来撤销结果。因此商家要在付款前后保留清晰订单说明、授权记录、交付证明和客服沟通，争议通知到达后立即处理后续业务影响。

## 上线测试清单

- Dashboard 已请求并获批 PayTo，身份验证已完成；
- 目标商家与客户均符合澳大利亚范围，币种为 AUD；
- 单笔金额未超过账户和客户银行限制；
- PayID 和 BSB/账户号码两种路径均已测试；
- 银行授权通知、批准和拒绝流程已验证；
- 一次性 Mandate 与订阅 Mandate 分别测试；
- 固定金额、最大金额、频率和有效期符合客户授权；
- 客户撤销 Mandate 后系统停止未来扣款；
- 延迟确认期间订单不会提前履约；
- PayID 退款检查银行账户姓名匹配；
- 争议 webhook 能及时通知财务和客服；
- 系统记录完整 Mandate、付款和退款对象关联。

## 总结

Stripe PayTo 允许澳大利亚客户通过银行应用或网银授权实时付款，也支持在 Mandate 条款范围内进行经常性扣款。接入需要澳大利亚账户和 AUD 交易，商家需完成额外身份验证，并遵守账户和银行的单笔限额。

重点是把 Mandate 当作明确的客户授权来管理：金额、周期、用途和期限都要符合客户同意内容；延迟付款要等待服务端确认；客户撤销授权时要停止扣款。PayTo 退款最长可在原交易两年内提交，PayID 退款还要检查姓名匹配；争议则无法申诉。将这些规则纳入后台、Webhook 和客服流程后再开放支付方式。

## 参考资料

- [Stripe：PayTo 支付方式说明](https://docs.stripe.com/payments/payto)
- [Stripe：PayTo PaymentIntent 参数](https://docs.stripe.com/api/payment_intents/create)
- [Stripe：Mandate 对象](https://docs.stripe.com/api/mandates/object)
- [Stripe：争议事件类型](https://docs.stripe.com/api/events/types)
