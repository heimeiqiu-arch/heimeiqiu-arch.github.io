---
title: "Stripe PaymentIntent 取消指南：可取消状态、授权释放与退款区别"
date: 2026-11-15
slug: "stripe-paymentintent-cancel-status-authorization-release-refund-guide"
description: "介绍 Stripe PaymentIntent 哪些状态可以取消、requires_capture 时如何释放剩余授权，以及 Checkout Session 过期和已付款退款的处理区别。"
keywords:
  - Stripe PaymentIntent 取消
  - PaymentIntent cancel
  - requires_capture 释放授权
  - Stripe Checkout 过期
  - Stripe 取消与退款区别
tags:
  - Stripe
  - PaymentIntent
  - Checkout
  - 退款
---

取消 Stripe 支付时，最常见的误区是把“取消 PaymentIntent”“释放银行卡预授权”和“向客户退款”当成同一件事。它们对应不同的支付状态和资金路径：还没有成功收款的 PaymentIntent 可以在允许状态下取消；手动捕获订单取消时，未捕获的授权金额会被释放；已经成功扣款的交易则通常要创建 Refund，而不是尝试取消 PaymentIntent。

本文说明 Stripe PaymentIntent 的可取消状态、Checkout Session 的特殊处理方式，以及订单系统如何避免误取消或重复退款。操作前先读取 PaymentIntent 当前状态和关联 Checkout Session，不能仅依据本地订单标签执行 API 请求。

## 哪些 PaymentIntent 状态可以取消

Stripe 当前 API 文档允许在以下状态取消 PaymentIntent：

- requires_payment_method；
- requires_confirmation；
- requires_action；
- requires_capture；
- 在少数情况下的 processing。

取消成功后，PaymentIntent 进入 canceled 状态，不会再由该 PaymentIntent 发起新的收费操作；对已取消对象的后续操作会报错。若对象已经处于不允许取消的状态，API 会返回错误。

requires_capture 表示付款已完成授权但尚未捕获。取消该 PaymentIntent 时，未捕获的 amount_capturable 会自动释放或退回给客户的支付方式。银行释放预授权的显示时间由发卡行或支付方式决定，商家不应承诺客户立即在账户中看到资金变化。

processing 状态的取消属于少数情况，通常与异步支付有关。不要假设所有处理中支付都能取消；应根据当前 PaymentIntent、付款方式和 Stripe 返回结果处理。如果交易已经完成，需要根据实际对象状态决定是否退款。

## 取消和退款的区别

**取消 PaymentIntent** 适用于支付尚未最终成功、且处于可取消状态的操作。它可以阻止该 Intent 后续继续收款；如果是未捕获授权，还会释放剩余授权金额。

**创建 Refund** 适用于已经成功收款的支付。Refund 是新的退款对象，有自己的 pending、succeeded 或 failed 等状态。退款可能需要一段时间才能到达客户账户，且不同支付方式的退款限制不同。

例如，一笔银行卡支付已显示 succeeded，商家收到客户取消订单请求，这时不应试图把 PaymentIntent 改成 canceled，而应按退款政策创建全额或部分 Refund。反过来，如果授权成功但尚未捕获，订单在发货前被取消，可能可以取消 PaymentIntent 并释放未捕获金额。应先核实 captured amount 和 amount_capturable，避免把已捕获部分当成可释放授权。

## Checkout Session 有单独的取消规则

Stripe 文档指出，Checkout Session 对应的 PaymentIntent 只有在 requires_capture 状态时，才可以直接取消 PaymentIntent。若 PaymentIntent 处于其他状态，商家应让 Checkout Session 过期，而不是直接对 PaymentIntent 调用 cancel。

这条规则能避免 Checkout 仍处于打开状态，而底层 PaymentIntent 被单独取消，导致前端页面和服务端对象不一致。订单取消时，应先检查 Checkout Session 当前状态、过期时间和 PaymentIntent 状态，再选择对应操作。

如果 Session 已完成，通常要根据支付结果执行退款或履约；如果 Session 仍打开，可按 Checkout 的过期流程结束它并更新内部订单。不要同时反复取消 PaymentIntent、过期 Session 和创建新订单，避免生成重复付款或状态冲突。

## 取消原因与审计

Cancel API 可附带 cancellation_reason，例如 duplicate、fraudulent、requested_by_customer 或 abandoned。应根据真实订单情况选择原因，方便后续分析和客服追踪；不要为了让错误看起来合理而随意使用 fraudulent 等标签。

建议内部订单记录保存：

- PaymentIntent ID 和 Checkout Session ID；
- 取消请求人和请求时间；
- 取消前的 PaymentIntent 状态；
- cancellation_reason；
- amount_received 与 amount_capturable；
- Stripe 返回结果和 webhook 事件；
- 是否需要创建 Refund 或重新创建 Checkout Session。

如果客户要求取消，记录客户通过哪个渠道提出请求以及对应订单。若因重复订单取消，先确定哪一笔支付有效，再分别处理未完成 Intent 和已经成功的支付，避免两个订单都被错误地取消或退款。

## 幂等、竞态与 Webhook

订单取消可能与付款确认同时发生。例如客服操作时，客户正在完成 3DS 或钱包授权；本地订单刚进入取消状态，Stripe 随后又收到付款成功事件。服务端需要用状态机处理这种竞态：

1. 读取最新 PaymentIntent 和 Session 状态；
2. 确认当前状态允许取消或过期；
3. 使用幂等请求或内部操作锁防止重复取消；
4. 记录 Stripe API 返回；
5. 处理支付成功、取消或过期的 webhook；
6. 如果付款事实上已成功，依据业务政策改走退款流程；
7. 将客户通知和履约系统同步到最终状态。

Webhook 事件可能重试或乱序到达。使用事件 ID 去重，并在处理时重新读取当前对象，不要只根据旧事件快照把订单从“已支付”退回“已取消”。对已经捕获的金额，取消后不能再把它视为已自动退款；必要时必须创建 Refund 并跟踪其最终状态。

## 常见错误

**对 succeeded 的 PaymentIntent 调用 cancel。** 已付款后通常应走退款流程，不能把收款历史删除。

**把 requires_capture 当成已退款。** 取消会释放未捕获授权，但银行端显示释放需要时间，也不等于发起一笔退款交易。

**Checkout Session 仍打开时直接取消底层对象。** 按 Stripe 文档的特殊规则处理 Session 过期，除 requires_capture 外不要直接取消对应 PaymentIntent。

**忽略处理中的异步付款。** processing 只有少数情况可取消，需看支付方式和 Stripe 实际状态。

**取消后不监听 webhook。** 页面状态、API 返回和后台事件可能存在时间差，最终订单状态要统一更新。

## 上线测试清单

- requires_payment_method、requires_confirmation 和 requires_action 状态取消；
- requires_capture 状态取消并核对 amount_capturable；
- succeeded 状态取消请求被正确转为退款流程；
- Checkout Session 打开时使用 expire API；
- Checkout Session requires_capture 时测试直接取消 PaymentIntent；
- 异步支付 processing 状态按当前方式单独验证；
- 重复取消请求不会创建错误状态或重复操作；
- 取消和付款成功 webhook 交错时订单状态正确；
- Refund 请求与最终退款状态分开记录；
- 客户通知能说明“授权释放”与“退款处理”的差别。

## 总结

Stripe PaymentIntent 只能在特定状态取消。常见可取消状态包括 requires_payment_method、requires_confirmation、requires_action 和 requires_capture；processing 只在少数情况允许。取消 requires_capture 对象会释放未捕获的授权金额，但不能代替对已成功付款创建 Refund。

如果 PaymentIntent 属于 Checkout Session，除 requires_capture 外，Stripe 要求先让 Session 过期。先读取 Session 和 PaymentIntent 当前状态，再按取消、过期或退款的正确路径处理，并通过 webhook 与 Refund 对象确认最终结果，能避免重复收费和错误退款。

## 参考资料

- [Stripe：取消 PaymentIntent API](https://docs.stripe.com/api/payment_intents/cancel)
- [Stripe：PaymentIntent 与 Checkout Session 生命周期](https://docs.stripe.com/payments/paymentintents/lifecycle)
- [Stripe：使 Checkout Session 过期 API](https://docs.stripe.com/api/checkout/sessions/expire)
- [Stripe：创建 Refund API](https://docs.stripe.com/api/refunds/create)
