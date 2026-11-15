---
title: "Stripe Checkout customer_creation 指南：always 与 if_required 的区别"
date: 2026-11-15
slug: "stripe-checkout-customer-creation-if-required-always-guide"
description: "比较 Stripe Checkout Session 中 customer_creation 的 always 与 if_required，说明访客结账、Customer 数据保存、优惠码和后续订阅的影响。"
keywords:
  - Stripe customer_creation
  - Checkout always if_required
  - Stripe Checkout Customer 创建
  - Stripe 访客结账
  - Checkout customer_details
tags:
  - Stripe
  - Checkout
  - Customer
  - 支付集成
---

在 Stripe Checkout 中收集客户信息，不一定会自动创建一个 Stripe Customer 对象。对于一次性付款，Session 可以只收集完成交易所需的邮箱、姓名和地址；如果商家还希望在 Stripe 中保留可检索的客户记录，就需要理解 customer_creation 参数。选错该参数可能让 CRM 找不到预期的 Customer，也可能为每笔交易创建大量只用一次的客户记录。

Checkout Session 的 customer_creation 有 always 和 if_required 两种设置。always 表示客户确认 Session 时始终创建 Customer；if_required 表示只有当前 Session 流程必须有 Customer 时才创建。对于 payment 模式，默认通常是 if_required；subscription 模式本身需要 Customer。未创建 Customer 并不代表 Checkout 没有收集用户资料，完成后的 Session 仍可提供 customer_details 等信息。

## Customer、customer_details 与 customer_email 的区别

Customer 是 Stripe 中可被多个对象引用的客户资料记录，通常用于关联订阅、发票和后续支付方式。Checkout Session 的 customer 字段指向这个对象。一次性付款如果没有必要持久化 Customer，Stripe 仍能在 Session 的 customer_details 中返回用户在结账时提供的资料。customer_details 是此次结账收集到的信息快照，不等同于长期客户档案。

customer_email 是创建 Session 时可传入的邮箱，主要用于预填结账表单，也可在创建 Customer 时作为其初始邮箱。它不是Customer ID，也不能替代自己的客户主键。客户可能更改邮箱，多个内部账号也可能共用一个邮箱地址，因此不应仅依赖邮件地址把 Stripe 付款匹配到用户账户。

若 Session 使用现有 customer 参数，Checkout 会使用已有 Customer。payment 模式下，客户的卡信息可能用于预填表单；subscription 模式则会依据默认支付方式等规则提供信息。已存在的 Customer Email 可能不能在 Checkout 页面编辑；如果没有有效邮箱，结账时输入的邮箱可能被写回该 Customer。更新行为应结合 customer_update 参数和商家期望审查。

## always 和 if_required 的行为

选择 always 时，Stripe 会在 Session 确认过程中创建 Customer。适合商家希望每次付款都沉淀为可查询客户记录、计划通过 Customer 对象关联收据或后续业务，且有能力管理客户生命周期的场景。创建后，应保存 Stripe Customer ID 与内部客户 ID 的对应关系，后续通过服务端检索和更新同一对象。

选择 if_required 时，Stripe 仅在完成 Session 必需 Customer 时才创建对象。Stripe 文档列出的情况包括 subscription 模式，以及启用了购后发票的 payment 模式 Session。其他一次性付款可以不创建 Customer，Dashboard 会将此类交易作为访客客户（guest customers）展示。Session 完成后仍能读取 Checkout 收集到的 customer_details，并据此处理订单联系信息。

如果使用了限定为首次客户的 Promotion Code，访客 Session 可能无法通过资格检查，优惠码会返回无效。这是因为“这次结账提供了一个邮箱”与“Stripe 识别出一个可判断新旧关系的 Customer”不是同一概念。促销逻辑依赖 Stripe Customer 身份时，应采用适合该业务的 Customer 创建策略，并实际测试优惠码规则。

## 访客结账适合什么时候

一次性匿名购买、数字内容单次付款或不需要账户体系的服务，通常可以让结账更轻量。系统收到 checkout.session.completed 后，从 Session 中取回自己的订单关联标识和客户联系资料，将资料存入商家自己的订单记录即可。Stripe 中不创建 Customer，并不会阻止商家给客户发订单确认邮件，但商家需要保留好所需的交易和客服信息。

若后续需要让用户登录查看历史订单，建议使用内部订单或账户 ID 与支付记录关联，而不是收到付款后仅按邮箱自动认领账户。客户可能在购买时填错邮箱，也可能把家庭或公司邮箱用于多人账号。账户认领应使用受验证的登录身份，并保留审计记录。

Stripe Dashboard 对访客客户的展示和商家自有 CRM 的客户模型也不是同一个东西。如果客服日常依靠 Dashboard 的 Customer 页面查找客户，那么创建 Customer 可以方便检索；如果所有客服操作都在自有系统进行，强制创建对象可能会产生大量低价值记录。设置前要考虑客服、报告、退款、发票和数据保留流程。

## 订阅、免费试用和后续扣款

subscription 模式需要 Customer 来关联订阅，所以不能简单用 if_required 的语义推断“永远不创建客户”。免费试用中 payment_method_collection 还控制是否在零金额阶段收集付款方式。即使当前账单为零，产品仍需决定试用结束时如何扣款：如果用户没有提供支付方式，订阅可以根据相关试用设置取消、暂停或生成发票。Customer 是否存在与 PaymentMethod 是否已经收集，是两个独立问题。

对于未来复用支付方式，商家要选择与预期用途相符的配置，并取得明确的用户授权。创建 Customer 本身不会自动等于已保存可用于离线扣款的卡片。一次性付款若未来需要保存支付方式，应配置相应的 setup_future_usage 或使用 SetupIntent 流程，并按照 Stripe 文档管理同意和后续认证。

当用户更改订阅、申请退款、更新付款方式或取消服务时，系统需要准确找到对应 Customer。如果用户只以访客方式完成一次付款，之后又注册了账户，不要盲目按邮箱合并记录；应通过账户验证、订单证据和商家数据策略决定是否将历史交易关联到新账户。

## 两个 collection 参数不要混淆

customer_creation 控制是否创建 Customer 对象；payment_method_collection 控制是否在 Checkout 收集支付方式。后者在 Checkout subscription 模式中有 always 和 if_required 选项。if_required 在总应付金额为零时可以不收集 PaymentMethod，例如免费试用或折扣覆盖全部金额的情况。即使客户信息收集字段仍然存在，也不意味着已收集银行卡。

因此，不能通过设置 customer_creation=always 来确保收集银行卡，也不能通过 payment_method_collection=if_required 来避免创建 Customer。应分别根据客户记录需求和后续收费策略设置这两个参数，并在 Session 创建响应及完成事件中检查实际对象。

## Webhook 与数据同步建议

建议在服务端创建 Checkout Session 时写入内部订单号、账户号或支付尝试号等 metadata 或 client_reference_id。Webhook 收到 checkout.session.completed 后，检索并核验 Session，将其与内部订单匹配；如果 Customer 已创建，则保存其 ID；如果没有，则从 customer_details 读取完成订单所需的联系资料。Session 对象和本地状态都应保留，避免后续无法判断客户记录是在什么时候建立的。

事件可能重复或延迟，因此 webhook 处理要验证签名，以事件 ID 去重，并确保同一 Session 的重复处理不会重复发货、重复记账或生成多条内部 Customer 映射。用户关闭成功页面不应导致订单漏记；浏览器返回的参数也不应单独作为收款证明。

对账时可以按 Session ID、PaymentIntent ID、Customer ID 和内部订单号分别查找。对访客订单，Customer ID 为空并不一定是错误；要结合 Session 的 customer_creation、mode 和实际支付结果判断。监控异常创建率、未映射 Customer、首次客户优惠码错误以及重复账户等指标，更容易发现参数配置与业务流程不一致的问题。

## 常见配置误区

**以为Checkout收集邮箱就必然会创建Customer。** Session 资料和 Customer 对象是两个不同层级的数据。

**认为if_required一定不会创建Customer。** 订阅模式和购后发票等场景需要 Customer，仍会创建。

**给所有一次性访客付款强制创建Customer。** 如果不需要后续账户、发票或客户管理，持续创建记录会增加数据维护成本。

**认为always意味着PaymentMethod已保存。** Customer 存在不代表银行卡已经附加，也不代表获得未来离线扣款授权。

**把邮箱当成不可变用户ID。** 邮箱可以更改或共享，账户归属应基于已验证的内部身份。

**试图用if_required处理首次客户折扣。** 访客交易没有 Customer 身份时，依赖首次客户判断的 Promotion Code 可能无效。

## 上线前核对清单

- 明确一次性付款是否需要在 Stripe 中创建 Customer；
- 确认现有 Customer ID 与内部账户 ID 有稳定映射；
- 了解 subscription 和购后发票创建 Customer 的要求；
- 将 customer_creation 与 payment_method_collection 分别配置；
- 确认客户资料从 Session、Customer 还是内部数据库读取；
- 若使用首次客户优惠码，测试访客和现有客户两种路径；
- 若未来复用支付方式，另外配置相应流程并收集授权；
- Webhook 依据 Session ID 幂等更新订单和客户映射；
- 对账时允许访客订单没有 Customer ID；
- 检查客服、退款和发票流程是否依赖 Customer 对象。

## 总结

customer_creation 决定 Checkout Session 是否在结账确认时创建 Stripe Customer。always 适合需要持久化每笔付款客户对象的业务；if_required 则让无需 Customer 的一次性付款以访客方式完成。访客 Session 仍会保留 Checkout 收集的 customer_details，但这些资料不会自动变成长期 Customer 档案。

配置时也要区分 Customer 创建与银行卡收集。subscription 模式或购后发票可能要求 Customer，而 payment_method_collection 则决定是否要求填写支付方式。通过内部订单标识、Webhook 和明确的数据映射同步付款及客户资料，才能兼顾简洁结账和后续客户服务。

## 参考资料

- [Stripe API：创建 Checkout Session](https://docs.stripe.com/api/checkout/sessions/create)
- [Stripe：Checkout 访客客户](https://docs.stripe.com/payments/checkout/guest-customers)
- [Stripe：Checkout 免费试用](https://docs.stripe.com/payments/checkout/free-trials)
- [Stripe：保存支付方式以供未来使用](https://docs.stripe.com/payments/save-and-reuse)
