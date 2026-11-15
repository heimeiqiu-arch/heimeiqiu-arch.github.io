---
title: "Stripe Checkout 延迟付款指南：async_payment Webhook 与订单履约"
date: 2026-11-15
slug: "stripe-checkout-delayed-payment-async-webhook-fulfillment-guide"
description: "解释 Stripe Checkout 中 Session 完成与资金确认的区别，使用异步付款成功或失败事件驱动发货、数字权益和库存状态。"
keywords:
  - Stripe Checkout 延迟付款
  - checkout.session.async_payment_succeeded
  - checkout.session.async_payment_failed
  - Stripe 异步付款 webhook
  - Checkout 延迟确认履约
tags:
  - Stripe
  - Checkout
  - Webhook
  - 延迟付款
---

在 Stripe Checkout 中，客户提交付款并离开结账页面，不一定代表资金已经到账。银行卡等即时支付方式通常较快返回结果，而银行借记、转账或现金凭证等延迟付款方式可能需要更久确认。对于这些方式，Checkout Session 可以先完成结账流程，付款仍处于处理中；系统若在此时立刻发货或开放数字权益，就可能出现付款后来失败、商品已经交付的情况。

延迟支付的核心是区分 Checkout 流程状态与实际付款状态。checkout.session.completed 表示客户已完成结账流程；对于延迟确认方式，Stripe 之后还会发送 checkout.session.async_payment_succeeded 或 checkout.session.async_payment_failed。服务端应以签名验证后的 Webhook 和 Stripe 对象状态驱动最终履约，而不是只依赖 success_url 的浏览器跳转。

## Session complete 不一定表示已付款

Checkout Session 有 status 和 payment_status 等不同字段。status=complete 说明客户已完成 Checkout 流程，但 payment_status 仍可能是 unpaid 或 processing。即使用户看到“感谢购买”页面，也要根据当前支付方式判断是否可以立即履约。

对于延迟付款，Stripe 可能在资金确认前将 PaymentIntent 置于 processing。此时订单应保持待付款或处理中，显示清楚的预计确认提示。不要显示“付款失败”，也不要显示“已成功付款”。客户已完成的操作可以作为结账已提交的证据，但不能作为款项已经结算的依据。

当资金之后成功时，Stripe 发送 checkout.session.async_payment_succeeded。该事件可作为触发履约的信号之一，服务端仍应读取 Checkout Session 或 PaymentIntent，确认 payment_status 和关联订单。若最终失败，checkout.session.async_payment_failed 可用于把订单转为付款失败、通知客户，或提供另一个付款方式。

## 设计服务端订单状态

不要只用 paid=true/false 表示所有情况。可以为订单定义待付款、支付处理中、支付成功、付款失败、退款处理中、已退款等状态，并为一次订单关联支付尝试 ID。这样付款方式延迟时，客服和用户都能知道订单尚未完成，而不是误以为系统漏单。

创建 Checkout Session 时保存 Session ID 和内部订单号。Webhook 到达时，依据 Session ID 找到对应支付尝试，不要仅按邮箱或金额关联订单。同一客户可能同时创建多个订单，同一金额也可能出现在很多订单中。metadata 或 client_reference_id 可以帮助对账，但最终商品、金额和客户归属应来自服务端订单记录。

库存预留策略应结合支付方式确认时间设计。预留太短可能在银行处理期间释放库存，客户付款成功后商品却已无货；预留太长则会占住库存，降低其他客户购买机会。高需求产品可把库存预留设为有期限的状态，并在支付确认成功时原子地扣减库存，在失败或明确超时后释放。

## Webhook 监听和幂等处理

生产环境需要建立服务端 Webhook endpoint，监听 Checkout 的付款事件。至少根据业务支持的支付方式监听 checkout.session.completed、checkout.session.async_payment_succeeded 和 checkout.session.async_payment_failed。实际需要哪些事件，应查看当前使用的支付方式及其确认机制，并在 Dashboard 或 API endpoint 配置中启用。

接收事件时先用 Stripe SDK 验证签名，再解析事件类型和对象 ID。保存 Event ID 并做去重，避免 Stripe 重试或多个触发路径导致重复发货。履约函数必须能被相同 Session ID 重复、安全地调用。可在数据库中使用唯一约束，确保每个订单只生成一次发货任务或权益授予。

Webhook handler 要快速返回成功响应，把较重的工作放到后台队列。若发货系统暂时不可用，可以让队列重试；重试时再次读取订单状态，并检查是否已经完成履约。这样即使 Stripe 重新发送相同事件，系统也不会重复扣库存或重复发送授权邮件。

不要假设事件一定按创建顺序到达。付款成功事件可能晚于用户页面访问，也可能 Webhook delivery 延迟。事件处理时可把事件作为触发检查的线索，再从 Stripe API 拉取当前 Session 和支付对象状态，并用明确的允许转换表更新本地订单。

## 付款成功后执行履约

服务端确认款项成功后，可以履行 Session line_items：创建出库单、扣减最终库存、开通数字内容、启动订阅权益或发送订单通知。履约前要从 Stripe 拉取 line_items，避免仅信任浏览器传回的购物车数据。若允许用户在 Checkout 中调整数量，必须以最终 Session 行项目为准。

对 subscription 模式，要同时考虑订阅生命周期与首张发票状态。付款成功并不意味着订阅永远有效，后续续费仍可能失败或取消。对一次性商品，履约后也应保存订单行项目、数量、金额、税费和币种快照，方便售后及财务对账。

如果业务希望客户提交付款后立即展示确认页面，可以展示“已提交，等待支付确认”的状态，而不立即交付。之后成功事件到达再更新页面；如果失败，则发送补付说明。用户可能不会再次打开网站，因此邮件或站内通知要设计合理，同时避免在未付款时发送最终发货通知。

## 失败后的客户处理

收到 async_payment_failed 后，先将该支付尝试标记为失败并核对订单是否已有其他有效支付尝试。向客户说明付款未完成，提供继续付款、选择其他方式或联系支持的入口。不能在没有检查原 PaymentIntent 状态的情况下立即创建另一笔扣款，以免支付后来被确认成功造成双重付款。

延迟付款失败与 Checkout Session 过期是不同问题。Session 可以已 complete，但付款失败；反过来，Session 过期事件也不等同于某笔银行付款已最终失败。订单状态机应保存两类事件，并按具体 Session ID 和 PaymentIntent 状态判断后续动作。

如果客户已经付款，但履约系统有短暂故障，不要让客户重新付款。保留成功 PaymentIntent 与内部订单的关联，重试履约任务，而不是创建新的 Checkout Session。对账任务可以定期扫描长时间处于 processing 的支付，核对 Stripe 当前状态并修复内部订单状态。

## 客户页面和信息传达

Checkout success 页面不应只写“订单已完成”。对即时方式，服务端确认后可以显示已支付；对延迟方式，可以显示“付款正在确认，确认后会通知您”。页面可使用 Checkout Session ID 请求商家服务器查询状态，但不能让浏览器直接决定订单状态。

成功页面的 Session ID 不是秘密凭证，也不能代替身份验证。页面接口要验证当前登录用户是否有权查看该订单，避免仅猜测 Session ID 就获取地址、邮箱或发票资料。显示的订单详情应与服务端记录一致。

可以建立邮件通知规则：Checkout 完成时发“已提交付款”的说明；异步成功时发“已确认付款”的通知；异步失败时发补付提示。不同支付方式的银行处理时间差异较大，文案应避免承诺固定到账时间，具体以实际方式和地区为准。

## 测试场景与上线核对

在测试环境中覆盖即时卡支付成功、延迟支付处理中、延迟成功、延迟失败、Webhook 重复投递、Webhook 延迟、发货系统超时和客户未访问成功页面。使用 Stripe CLI 转发测试事件，验证每个事件触发的订单状态转换，并确认相同事件重复送达不会重复履约。

上线前确认：

- 订单状态区分结账完成、处理中、已付款和失败；
- 创建 Session 后保存 Session ID 与内部订单 ID；
- 服务端验证 Webhook 签名和事件去重；
- 处理 checkout.session.completed 与两个 async_payment 事件；
- 使用 Stripe 当前对象状态确认资金结果；
- 履约函数对相同 Session ID 幂等；
- 库存预留和释放能够处理长时间处理中；
- 失败事件不会覆盖已成功的其他支付尝试；
- 客户页面清楚区分已提交与已确认；
- 通过后台任务处理重试，不在浏览器中重试扣款。

## 总结

对于 Stripe Checkout 延迟付款方式，客户完成 Session 并不总是资金已成功。checkout.session.completed 表示结账流程完成；支付稍后成功或失败时，Stripe 使用异步付款事件通知商家。订单、库存和权益都应根据服务端核实的支付状态推进。

实现时保存 Session 与内部订单关联，验证并去重 Webhook，使用幂等履约函数，并为处理中状态设计客户通知和库存策略。这样可以避免资金尚未确认就发货，也能避免支付后来成功时要求客户重复付款。

## 参考资料

- [Stripe：Checkout 履约指南](https://docs.stripe.com/checkout/fulfillment)
- [Stripe API：事件类型](https://docs.stripe.com/api/events/types)
- [Stripe：延迟通知支付方式](https://docs.stripe.com/payments/payment-methods)
- [Stripe：Checkout Session 对象](https://docs.stripe.com/api/checkout/sessions/object)
