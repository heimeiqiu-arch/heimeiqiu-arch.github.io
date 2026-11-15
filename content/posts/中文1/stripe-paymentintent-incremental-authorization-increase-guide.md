---
title: "Stripe PaymentIntent 增额授权怎么用：incremental authorization 与失败回退"
date: 2026-11-15
description: "Stripe 增额授权指南：说明 PaymentIntent 适用状态、incremental_authorization_supported、递增目标金额、失败处理，以及增额授权与多次捕获的区别。"
slug: stripe-paymentintent-incremental-authorization-increase-guide
tags:
  - Stripe
  - PaymentIntent
  - 增额授权
  - incremental authorization
  - 手动捕获
keywords:
  - Stripe 增额授权
  - Stripe incremental authorization
  - PaymentIntent increment_authorization
  - incremental_authorization_supported
  - Stripe 延长预授权金额
---

# Stripe PaymentIntent 增额授权怎么用：incremental authorization 与失败回退

酒店押金、租车、餐饮消费或其他先估算、后确认金额的场景中，商户可能在最初授权后发现最终账单会更高。常见想法是直接把 PaymentIntent.amount 改大，但已经授权的卡交易并不能按普通数据库字段那样任意修改。对于满足条件的 PaymentIntent，Stripe 提供增额授权流程，让商户尝试提高卡上的授权金额，再根据实际履约捕获资金。

增额授权不是保证成功的“补差额扣款”，也不是多次捕获。发卡行可能拒绝新的增额授权；可用性还取决于账户、卡片、网络和交易流程。本文讲解 eligibility 字段、increment_authorization 的基本含义、失败后如何避免误捕获，以及怎样区分增额授权和 multicapture。

## 增额授权与初始授权的关系

初始授权为卡交易申请一个金额，客户的发卡行可能批准或拒绝。增额授权则在符合条件的已授权 PaymentIntent 上，请求把授权总额提高到一个新的、更高金额。它不是另建一个独立付款，也不是把金额差额自动变成第二笔交易。

Stripe 文档指出，增额授权要求 PaymentIntent 处于 requires_capture 状态，且其 incremental_authorization_supported 属性为 true。创建 PaymentIntent 时还可以按当前 API 文档请求 incremental authorization 支持；请求支持并不能保证具体交易一定符合条件。服务端应读取 Stripe 返回的资格状态，不要只根据付款方式类型或商户自认为的场景判断。

如果业务预计最终金额会上升，例如酒店入住期间增加服务，建立完整流程前应先确认当前账户和目标支付方式能否使用增额授权。对于未支持的交易，应提供另一个付款方案，例如取得新的付款同意、生成额外的 PaymentIntent，或使用适合该场景的结账流程。不要在客户不知情时悄悄创建新的额外扣款。

## amount 表示目标授权总额

调用增额授权 API 时，传入的 amount 是希望新的授权达到的金额，而不是“额外增加多少”的差额。比如当前授权总额是 100，最终估算升到 130，请求的新金额应表达 130，而不是 30。调用前先读取 PaymentIntent 当前金额和状态，使用服务端订单数据计算新的总额，并核实币种和金额精度。

把增额授权请求作为独立的业务动作记录，包括原始授权金额、目标总额、增额原因、发起人、订单状态和 Stripe 请求 ID。顾客账单或后台活动记录中也应能解释为什么授权金额发生变化。为重复请求提供内部幂等控制，避免操作员双击按钮导致同一订单同时发起多个增加请求。

请求成功后，以 Stripe 返回的 PaymentIntent 当前对象为准，刷新本地授权总额和 amount_capturable 等字段。请求失败时，Stripe 文档说明可能返回 card_declined，且 PaymentIntent 或 Charge 不会因此更新；因此不要继续按新金额捕获，也不要把失败请求当作已批准。向客户说明授权增加失败，依据业务规则请求客户更换支付方式、减少订单或重新完成付款。

## 增额授权与 Multicapture 不同

增额授权尝试提高顾客卡上的授权总金额；Multicapture 则在支持的条件下，对已授权资金进行多次捕获。一个解决“最终金额比最初预计更高”的问题，另一个解决“授权资金按多个阶段收取”的问题。二者都可能在手动捕获流程中出现，但不能互相替代。

如果订单总额仍在原始授权额度内，只是需要分批捕获，先确认 multicapture 资格与每次 capture 的 final_capture 设置；不需要为此提升授权总额。如果预计总金额超过初始授权，则增额授权请求应在捕获之前进行；若没有资格或增额失败，再按业务和顾客同意情况选择其他付款方式。

常见误区是先捕获初始部分金额，再试图为剩余部分增加授权。捕获会改变 PaymentIntent 的可捕获状态和后续操作边界；增额授权要求特定状态。流程应该按“创建并确认初始授权—读取资格—必要时增额—确认最终金额—捕获”的逻辑设计，并在代码中通过 PaymentIntent 当前状态阻止不合规操作。

## 订单和授权状态机设计

本地状态最好区分待授权、已授权待履约、增额请求处理中、增额成功、增额失败、部分捕获、最终捕获和取消。不要只保留一个 authorization_amount 字段覆盖旧值；保存授权历史可以让客服解释客户何时看到过哪些待处理金额，也可以帮助审计误操作。

当商户通过多个后台界面修改订单时，必须避免两个操作员同时用旧金额计算不同目标总额。数据库层面锁定订单或使用版本号比较更新，并将“读取现状—计算新总额—提交 Stripe 请求—同步响应”作为受控工作流。若网络超时，先查询 PaymentIntent 当前对象，再决定是否重试；不要为了得到明确结果直接发起第二笔付款。

Webhook 可能与 API 响应同时或先后到达。使用事件 ID 幂等处理，并以 Stripe 当前对象状态进行状态收敛。记录增额前后的金额，避免事件重放时再次将金额加一遍。对 Connect 平台，还要确认 PaymentIntent 属于正确的平台或 connected account 上下文，并核对费用和资金流是否符合该账户的交易结构。

## 失败后的客户体验和回退方案

增额授权被拒绝时，客户不一定需要从头重新购买，但系统要判断当前原授权是否仍然有效、原金额是否仍可捕获、商品是否可以按原范围履约。不要在未确认发卡行结果时发送“扣款失败”通知，也不要把原支付对象自动取消后立刻重试，可能造成重复授权提示。

依据业务条件选择回退：
- 若顾客可以缩小订单，将金额调整回已授权范围，再按 Stripe 支持流程捕获。
- 若必须支付更高总额，请客户重新确认交易或更换付款方式。
- 若业务允许分笔付款，说明新增付款如何与原订单关联，并防止重复发货。
- 若订单无法继续，取消或结束相关流程，并向客户说明待处理授权释放可能需要时间。
- 若 API 状态未知，先查询 Stripe 对象和事件记录，再联系 Stripe 支持或进入人工队列。

具体能否减少授权金额、继续原流程或重新使用同一 PaymentIntent，必须符合当前对象状态和 Stripe 文档，不能只凭通用支付知识推断。

## 测试和监控

在测试环境覆盖支持增额的成功交易、不支持的 PaymentIntent、请求金额不高于当前授权、增额被拒、API 超时和并发请求。测试资格要通过实际 PaymentIntent 的 incremental_authorization_supported 字段确认；测试卡和沙盒行为不一定覆盖生产中所有发卡行结果。

正式部署后监控增额请求数量、成功率、失败原因、原始金额与目标金额、后续捕获金额和交易最终状态。异常包括大量重复请求、目标金额突然大幅上升、增额失败后仍继续捕获高金额，以及用户投诉不认识授权金额变化。对这类交易保留操作员与订单审计记录，必要时提供客服可读时间线。

## 总结

Stripe 增额授权是在符合资格的 PaymentIntent 上请求更高的授权总额。调用前确认状态为 requires_capture 和 incremental_authorization_supported 为 true；amount 传新的总金额；失败时以 Stripe 对象未更新为事实，不能捕获未授权的高金额。将增额授权与 Multicapture 分开设计，通过订单锁、状态历史、幂等和客户回退方案减少重复授权与意外扣款。

请查看 Stripe 的[增额授权指南](https://docs.stripe.com/payments/incremental-authorization)、[PaymentIntent 增额授权 API](https://docs.stripe.com/api/payment_intents/increment_authorization)、[PaymentIntent 对象](https://docs.stripe.com/api/payment_intents/object)和[捕获 API](https://docs.stripe.com/api/payment_intents/capture)。
