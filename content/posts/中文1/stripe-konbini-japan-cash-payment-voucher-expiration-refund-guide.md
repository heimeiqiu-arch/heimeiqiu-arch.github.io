---
title: "Stripe Konbini 日本便利店现金支付：付款凭证、异步确认与退款"
date: 2026-11-15
slug: "stripe-konbini-japan-cash-payment-voucher-expiration-refund-guide"
description: "Stripe Konbini 如何收取日本 JPY 现金付款，配置便利店凭证有效期、区分 checkout.session.completed 与实际付款，并处理需客户提供银行信息的退款。"
keywords:
  - Stripe Konbini
  - Stripe 日本便利店支付
  - Konbini 付款凭证
  - Stripe Konbini 退款
  - checkout.session.async_payment_succeeded
tags:
  - 支付方式
  - 日本
---

Konbini 是日本便利店现金支付方式。客户在线下单后，会得到适用于指定便利店链的付款代码和确认编号，再到 FamilyMart、Lawson、Ministop 或 Seicomart 门店现金付款。商家在生成凭证时并未收到款项。Stripe 的 Checkout Session 进入 completed 也只表示客户提交了结账表单、Stripe 生成了付款凭证，并不代表顾客已在便利店付款。

Konbini 退款的流程同样特殊：Stripe 会联系客户索取银行账户资料，再通过银行转账退回款项。退款可能在资金已到客户账户后仍显示 pending，直到银行的失败报告窗口结束才变为 succeeded。本文说明日本账户资格、付款凭证有效期、异步确认、库存和订单管理、客户资料与退款处理。上线前请核对 Stripe Dashboard 和官方最新文档。

## 账户资格和付款限制

Konbini 面向日本客户，交易币种为 JPY。Stripe 文档列出的最低金额为 120 JPY、最高金额为 300,000 JPY。商户账户需要位于日本，企业还需符合 Stripe 和合作便利店机构的业务限制。行业禁限清单覆盖部分金融、烟草、博彩、成人、转售及其他类别；适用要求可能变化，申请时应检查完整列表。

网站资料也需要满足日本业务审核要求，例如公开可访问，显示经营地址、联系邮箱与电话、商品或服务、运费、客服时间、退款政策、付款流程以及日本《特定商取引法》要求的披露内容。个体经营者可能还需要展示注册经营地址的实体店或办公场所照片。若接受订阅发票，网站应明确显示重复收费、取消方式、起始和取消时的费用处理。

Konbini 支持一次性现金支付，不支持 off-session 自动扣款、保存支付凭证或 Checkout subscription mode。Hosted Invoice 可在使用 send_invoice 的情况下让客户每期到便利店支付；这不是自动续费，客户必须每张账单重新完成现金付款。

## 付款代码和有效期

客户选择 Konbini 后提供姓名和邮箱，可选提供电话号码作为确认编号。Stripe 为支持的便利店生成相应付款代码、确认编号和到期时间。默认期限为三个日历日，截止到到期日期日本时间 23:59:59；PaymentIntent 支持在 1 到 60 天范围内配置有效期。有效期应与库存保留和订单取消政策一致。

创建凭证后，订单应进入“等待线下付款”。保存各便利店类型的付款代码和确认编号，安全地展示或发送付款说明，并记录凭证创建时间和到期时间。客户需要在有效期内把适用代码带到对应便利店付款；到店付款后会获得纸质收据，但后台仍需等待 Stripe 的成功通知。

当凭证过期且客户未付款时，释放库存或关闭订单，并提示客户重新结账。重新生成付款码前，查询原 PaymentIntent 当前状态，避免客户已经付款但 Webhook 延迟到达而又开出新凭证。对同一订单的多次付款尝试保留关联，防止重复履约和漏处理款项。

## 关键事件：Session completed 不代表已收款

Konbini 的异步性质要求把凭证签发和现金付款成功分成不同状态。Stripe 发出 checkout.session.completed 时，含义是客户已提交 Checkout 表单，Session 完成了凭证创建流程；它不代表客户完成了门店付款。实际现金付款确认后，Stripe 会发送 payment_intent.succeeded；Checkout 集成还会发送 checkout.session.async_payment_succeeded。

履约应等待 payment_intent.succeeded 或 checkout.session.async_payment_succeeded，并验证对应订单和金额。收到支付成功事件后保存 Event ID，核对 PaymentIntent ID、订单号、金额、币种、Customer 和之前凭证状态，再发货、开通数字权益或发送收据。Webhooks 应签名验证和幂等处理，防止重试导致重复发货。

对于未付款、付款超时和支付失败，订单保持待付款或过期状态；客服可以查看 Stripe Dashboard 的 PaymentIntent 状态和凭证信息，不应仅凭客户的便利店纸质小票或邮件截图将订单标成已收款。若 Stripe 尚未确认，而客户确实已付款，记录门店、时间、金额和收据并按官方处理流程核查，不要擅自绕过 Stripe 状态。

## 退款必须向客户收集银行信息

Konbini 支持全额和部分退款，Stripe 文档当前允许在原付款后 730 天内发起。退款流程会由 Stripe 给客户发送邮件，要求提供退款银行账户资料；客户提交有效信息后 Stripe 才能发起银行转账。Stripe 不能在原支付资金尚未可用之前发送退款，因此总耗时还取决于资金可用时间和客户何时提交账户信息。

客户尚未提交银行信息时，Refund 可能处于 requires_action，此时商家可以按 Stripe API 规则取消退款。Stripe 已开始处理且状态变成 pending 后，就不能再取消。退款状态变为 pending 后，即使客户已经收到资金，Stripe 也可能需要等待银行失败报告期结束才把状态更新为 succeeded。客服不要把 pending 直接解释为“客户还没收到钱”，也不能因客户说收到款就跳过财务最终状态。

退款失败后，Stripe 会把相关金额返回 Stripe 余额，商家需要通过其他方式把款项退给客户。监听 refund.updated 和 refund.failed，保存 Refund ID、原付款、客户是否提交账户信息、最终退款方式、客服通知和处理人员。银行资料只通过合适的安全流程收集，不要让客户把完整账号直接发在普通客服邮件或公开表单中。

## 便利店凭证不是交易流水参考

现金付款不会在客户银行卡或银行流水中产生一笔卡片交易。因此，卡片 statement descriptor 不会出现在便利店付款凭证上。Stripe 显示的付款代码和确认编号是客户完成线下付款的说明，不是付款之后的银行交易 ID。

可从 PaymentIntent 的 next_action.konbini_display_details 中读取各便利店链的 payment_code 和 confirmation_number。客服可用订单号、PaymentIntent ID、便利店类型、凭证金额和付款时间进行查找。客户付款后，内部系统仍以 Stripe PaymentIntent、Charge 和 Balance Transaction 做财务关联，而不是把付款凭证号码当作已结算流水 ID。

资金可用时间与付款确认也不同。Stripe 文档说明 Konbini 付款资金在店铺付款确认后通常四个工作日后可用于 payout；银行到账还要看 Stripe 账户 payout 排程。将客户已支付、余额待结算、余额可用和已向银行打款分开显示，避免客户把便利店小票日期当成银行卡到账时间。

## Connect 和发票收款

日本平台可以使用自己的 Konbini activation 为 destination charge 或 separate charges and transfers 处理款项，并可能由平台账户收款结算；具体安排不能设置 on_behalf_of。此时 connected account 不一定需要单独启用 Konbini，但平台需核实适用的交易模型和账户责任，并确保客户看到的付款凭证信息与 merchant of record 一致。

订阅发票场景需要谨慎设置。Konbini 不支持 Checkout subscription mode 或自动扣款，但 Hosted Invoice 可以在 collection_method=send_invoice 时供客户现金支付。客户需为每一张发票单独支付，不是自动续费。如果使用 Konbini 收取订阅账单，设置合适的付款期限、服务宽限规则和未付款处理，并明确在网站展示每期金额和取消条款。

## 常见故障排查

**订单在凭证生成后就被标成已支付。** 检查履约是否错误使用 checkout.session.completed。改为等待 payment_intent.succeeded 或 checkout.session.async_payment_succeeded。

**客户付了现金，系统仍显示待付款。** 查询 PaymentIntent、Webhook 投递记录和门店付款时间；核对金额、代码和确认编号，并考虑 Stripe 异步通知过程。

**客户说退款已到账但 Stripe 仍为 pending。** 可能还在等待银行失败报告窗口结束。查看 Refund 状态与客服沟通，按最终事件更新财务结果。

**退款一直等待客户提供银行资料。** 检查 Stripe 发出的退款邮件地址、垃圾邮件和客户账户信息；提醒客户通过 Stripe 提供的流程安全提交。别通过不受保护的普通消息收集完整银行数据。

**凭证过期后客户重新支付。** 先核对旧 PaymentIntent 最终状态，再创建新尝试；如果旧款后来确认成功，触发异常重复付款处理，不要重复发货。

## 上线验证清单

测试凭证生成与邮件、3 日默认和自定义有效期、客户未付款过期、到门店付款后的成功事件、Session completed 但未支付、重复 Webhook、退款 requires_action、客户提供银行账户、退款 pending 到最终成功，以及退款失败后的替代付款流程。检查网站特定商业交易法披露、运费、退款政策、客服信息、网站资料与账户审核一致。

Konbini 能覆盖习惯现金付款的日本消费者，但商家必须把凭证和实际付款分开，等待 Webhook 确认后才履约。退款需要客户主动提供银行资料且处理期可能较长；将状态、客户动作、资金可用时间和替代退款记录纳入设计，才能避免现金支付订单长期悬而未决。

## 官方资料

- [Stripe：Konbini 支付](https://docs.stripe.com/payments/konbini)
- [Stripe：Konbini 收款接入](https://docs.stripe.com/payments/konbini/accept-a-payment)
- [Stripe API：创建退款](https://docs.stripe.com/api/refunds/create)
- [Stripe API：取消退款](https://docs.stripe.com/api/refunds/cancel)
- [Stripe：Checkout 履约](https://docs.stripe.com/checkout/fulfillment)
