---
title: "从 Stripe Charges API 迁移到 PaymentIntents：对象映射、Webhook 与分批切换"
date: 2026-11-15
description: "Stripe Charges API 迁移指南：梳理旧 Charge 流程与 PaymentIntent 的差异，制定订单字段映射、Webhook 更新、测试和逐步切换方案。"
slug: stripe-charges-api-to-paymentintents-migration-guide
tags:
  - Stripe
  - Charges API
  - PaymentIntents
  - API 迁移
  - Webhook
keywords:
  - Stripe Charges API 迁移
  - Stripe PaymentIntents 替代 Charges
  - Stripe Charge PaymentIntent 对象映射
  - Stripe 支付 API 升级
  - Stripe Webhook 迁移
---

# 从 Stripe Charges API 迁移到 PaymentIntents：对象映射、Webhook 与分批切换

较早的 Stripe 集成可能直接使用 Charges API 创建和确认付款。随着支付方式、客户认证和支付状态流程变得更复杂，PaymentIntents 成为现代支付集成的主要对象。迁移并不是把代码里的 Charge 名称全局替换成 PaymentIntent：PaymentIntent 管理一次付款尝试的生命周期，可能经历认证、处理中、成功或失败；Charge 是与具体资金尝试相关的对象，两者承担不同职责。

如果项目只在代码中保留一个 charge_id 字段，迁移时很容易丢失旧记录、Webhook 不再更新订单，或者同一订单被旧、新两条付款路径重复处理。本文介绍如何盘点旧流程、建立对象映射、迁移事件处理器并分阶段发布。具体 API 参数和支持的集成方式要按 Stripe 当前文档与使用的 SDK 版本确认。

## 先盘点旧集成而不是直接改接口

迁移前搜索代码库中所有创建 Charge、确认支付、处理失败、退款、保存支付方式和发送收据的入口。一个系统可能同时有网页结账、移动端、订阅补款、客服后台、Payment Links 或 Connect 收款，不同入口的风险和依赖并不相同。先绘制一次典型付款流程：订单创建、支付对象创建、客户确认、Webhook 回调、发货、退款和财务对账。

为每个入口记录旧对象字段、API key 环境、Webhook 事件、错误处理和下游系统。特别检查：
- 哪些逻辑通过同步 API 响应判断成功？
- 哪些逻辑依赖 charge.succeeded 或 charge.failed 一类事件？
- 哪些数据仓库只保存 Charge ID 或 balance transaction ID？
- 退款和争议系统通过什么 ID 反查订单？
- 是否有重复创建 Charge 的重试逻辑？
- 客户认证或重定向流程在哪里完成？

先建立完整清单，可以发现只改主结账页会遗漏的后台补款或订阅入口。迁移工作应以业务流程为单位，而不是只以 API 文件为单位。

## Charge 与 PaymentIntent 的职责映射

PaymentIntent 表示一次付款意图和付款状态生命周期，可能包含一个或多个确认尝试；Charge 表示具体的一次资金尝试和相关交易信息。成功的 PaymentIntent 通常会关联成功的 Charge，但不能把对象 ID互换使用。退款、争议、账单明细、收据和余额交易可能仍引用 Charge 或其他对象，因此数据库应该能够同时保存 PaymentIntent ID 与 Charge ID。

建议订单表使用自己的内部 order_id 作为主键，再维护以下映射：PaymentIntent ID、相关 Charge ID、Checkout Session ID（如使用 Checkout）、Stripe Customer ID、Webhook event ID 和 balance transaction ID。每个字段可以为空或有多个历史值，取决于业务的重试与多次付款设计。不要把 PaymentIntent ID 写入只接受 Charge ID 的旧报表列并沿用原含义。

前端也要从“调用创建 Charge 后直接显示结果”迁移为“服务端创建 PaymentIntent，客户端按需要确认，服务端以最终状态更新订单”。具体何时创建、何时确认、是否采用 Checkout 或 Payment Element，取决于你的集成模式。先选一种 Stripe 官方支持的完整路径，不要把旧 Charge 的确认逻辑与 PaymentIntent 的状态逻辑拼在一起。

## 数据库和 Webhook 迁移

在新旧流程并存期间，数据库应允许订单记录同时保留 Charge 与 PaymentIntent 引用。先新增字段和索引，再部署能读取新旧字段的代码，最后逐步打开新付款路径。不要在新对象字段写入完成前删除旧字段，避免历史记录和财务报表立即失联。

Webhook 处理器要同时考虑新旧事件。新流程可能产生 PaymentIntent 生命周期事件以及相关 Charge 事件。为每种事件定义唯一业务责任：哪个事件负责把支付标为成功，哪个事件只更新尝试明细，哪个事件更新退款或争议。避免在 payment_intent.succeeded 和 charge.succeeded 两个处理器里各自发货。

事件处理应通过 Stripe event ID 幂等，并以服务端读取或验证的对象状态更新订单。事件可能重试或乱序到达，不能因为旧 Charge 事件晚到就把已成功的新 PaymentIntent 标回失败。也不能把一次旧付款尝试的失败误认为整个订单已失败，而订单的后续 PaymentIntent 其实已经成功。

对历史订单的回填可分批执行：从旧 Charge 关联信息和 Stripe API 查询出可对应对象的记录，写入新的映射字段，保留无法确定的行给人工核对。不要只根据金额、邮箱和时间窗口自动合并，因为同一客户可能在短时间内进行多笔相同金额付款。

## 分阶段上线和避免双重扣款

推荐采用增量式切换：
1. 为新对象和事件扩展数据库结构，先部署兼容旧、新数据的读取代码。
2. 在测试环境使用 PaymentIntents 验证成功、认证、拒绝、取消、Webhook 重试和退款路径。
3. 在内部或少量流量中启用新集成，保留明确的旧流程回退开关。
4. 观察新流程的付款成功率、requires_action、处理中订单、Webhook 延迟和重复订单指标。
5. 扩大流量后确认所有下游系统都读取新映射，再停止创建新的旧式 Charge。
6. 仍保留历史 Charge 查询和退款能力，直到旧交易的运营和财务需求结束。

不要同时让同一订单调用旧 Charge 创建接口和新 PaymentIntent 确认接口。通过订单版本或支付尝试 ID控制只存在一条有效付款路径。若客户端请求超时，先检查原支付对象和订单状态再决定是否新建；不要因为“没收到响应”就创建第二笔付款。

在新流程里，client_secret 只传给对应客户的客户端，不写入通用日志；服务端 secret key 则只留在服务器。金额、币种、订单引用由后端生成，不能信任浏览器提交结果。迁移期间这些安全边界应一并审查，而不是假定旧系统原有实现自然适用于新对象。

## 验证、报表和客服工具

财务与客服系统通常依赖旧 Charge 的 dashboard 链接或 ID。迁移后检查订单详情页、退款后台、邮件模板、客服搜索、数据仓库和每日对账任务。客服输入订单号时，应能查看关联 PaymentIntent、Charge、退款及最新状态，而不是只能找到新对象或旧对象之一。

报表字段应区分支付意图、付款尝试、实际 Charge、退款和余额交易。订单金额是商业订单总额；PaymentIntent amount 是付款流程的金额；Charge 和 BalanceTransaction 记录可能反映交易金额、手续费、净额和币种转换。不要把这些数值列都合并到“支付金额”一列导致报表误读。

迁移验收时选取代表性交易逐笔比对：旧系统订单 ID、新 PaymentIntent、最终 Charge、Webhook 日志、退款记录和 Dashboard 显示。对每条旧入口确认已切到新流程或有明确保留原因，并监控不认识的事件类型、没有 order_id 映射的对象和长时间停留在处理中状态的订单。

## 总结

从 Charges API 迁移到 PaymentIntents，需要把付款状态机、对象关联、Webhook、数据库、退款、客服和财务报表一起梳理。保留 Charge ID作为具体交易尝试的引用，新增 PaymentIntent ID作为付款生命周期的引用；先兼容读取，再分批切换，避免同一订单双重发起，并用 Dashboard 与内部账本逐笔核对。

请参阅 Stripe 的[接受付款指南](https://docs.stripe.com/payments/accept-a-payment)、[PaymentIntent API](https://docs.stripe.com/api/payment_intents)、[Charge API](https://docs.stripe.com/api/charges)和[Webhook 文档](https://docs.stripe.com/webhooks)。
