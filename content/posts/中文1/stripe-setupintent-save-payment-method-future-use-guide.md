---
title: "Stripe SetupIntent 怎么用？不收费保存银行卡与未来付款设置"
date: 2026-11-14
description: "Stripe SetupIntent 教程：在不立即收款时安全设置付款方式，选择 on_session/off_session 用途，处理客户同意、Customer 关联、认证与 Webhook。"
slug: stripe-setupintent-save-payment-method-future-use-guide
tags:
  - Stripe
  - SetupIntent
  - PaymentMethod
  - 保存付款方式
  - 订阅
keywords:
  - Stripe SetupIntent
  - Stripe 保存银行卡
  - Stripe off_session
  - setup_future_usage
  - Stripe PaymentMethod
---

# Stripe SetupIntent 怎么用？不收费保存银行卡与未来付款设置

有些业务需要先让客户添加支付方式，但暂时不收款：例如订阅试用期开始前收集银行卡、客户在个人中心更新默认付款方式，或未来账单需要在客户不在线时自动扣款。此时直接创建一笔 PaymentIntent 再“收零元”通常不是合适的设计。Stripe SetupIntent 专门用于设置和验证未来使用的付款方式，完成时不会创建一笔普通商品付款。

保存付款方式涉及客户同意、未来使用场景、认证要求和付款方式本身的复用能力。SetupIntent 成功也不代表未来每次扣款都会成功或免于验证。本文介绍 SetupIntent 与 PaymentIntent 的区别、`on_session` 与 `off_session` 的用途、客户与 PaymentMethod 关联、Webhook 同步和常见故障排查。集成前应查看 Stripe 对所选支付方式和账户地区的当前要求。

## SetupIntent 和 PaymentIntent 的区别

PaymentIntent 用于收取一笔付款，表示这笔支付的金额、币种、支付方式和状态；SetupIntent 用于设置将来可使用的付款方式，处理保存、验证和可能需要的客户操作。

| 对象 | 主要目的 | 是否收取本次订单金额 | 常见场景 |
|---|---|---|---|
| PaymentIntent | 完成本次付款 | 是，按 PaymentIntent 金额 | 商品结账、一次性服务、Invoice 支付 |
| SetupIntent | 设置未来可用的付款方式 | 不收取普通订单金额 | 保存卡片、更新付款方式、准备未来订阅扣款 |

不能把 SetupIntent 视为“付款已经预先批准”。它完成的是付款方式设置流程；未来实际扣款仍需要新的 PaymentIntent 或 Invoice 收款流程，并可能被发卡行拒绝、要求认证或受支付方式规则限制。

## 什么时候使用 SetupIntent

SetupIntent 适合客户明确要保存或验证付款方式、但当前没有待收款项的场景：

- 免费试用开始前收集续费付款方式；
- 在账户设置页添加一张新卡；
- 客户更换订阅默认支付方式；
- 预约或后续服务需要先验证支付方式；
- 保存符合条件的银行付款方式或完成必要的授权流程；
- 商家希望在未来由 Billing 创建账单，而不是现在收款。

如果客户当前正在购买商品并要立即付款，通常应使用 PaymentIntent，并在付款流程中根据客户同意设置未来使用用途。这样可以在一次客户流程中同时完成本次支付和保存付款方式的准备，不必先做一个零金额流程，再另做一次收费。

## 选择 on_session 还是 off_session

SetupIntent 的 `usage` 用来表达未来使用付款方式时客户是否预计在场：

- **`on_session`：** 只计划在客户处于结账或账户操作流程时使用该付款方式。
- **`off_session`：** 未来扣款时客户可能不在页面或应用中，例如订阅续费。

选择时应依据实际业务，而不是为了让后续扣款更容易就一律设置为 off_session。Stripe 会根据用途应用相应的准备流程和认证行为，但发卡行仍可能在未来要求客户完成额外认证。商家需要准备失败通知、返回结账、更新付款方式和重试方案。

如果使用 PaymentIntent 收款并同时保存付款方式，相关配置通常通过 `setup_future_usage` 表达；若使用 SetupIntent，则直接设置 `usage`。PaymentIntent 的保存参数和 SetupIntent 的用途字段概念相关但并非同一个 API 参数，避免把一个对象的字段直接复制到另一个对象。

## 关联 Customer 与 PaymentMethod

若希望付款方式用于现有客户的后续交易，创建 SetupIntent 时应关联正确的 Stripe Customer。SetupIntent 成功后，其 PaymentMethod 会按配置与账户/客户关系关联。若未关联客户，可能无法按预期在该 Customer 的 Checkout、订阅或门户中显示保存的付款方式。

安全的服务端流程：

1. 客户通过商家应用完成登录；
2. 后端根据登录用户查找已绑定的 Stripe Customer ID；
3. 校验 Customer 属于当前内部用户；
4. 后端创建关联该 Customer 的 SetupIntent，并选择适用的付款方式类型和 usage；
5. 将 SetupIntent 的 Client Secret 安全地返回给当前用户；
6. 前端使用 Stripe.js 或对应 SDK 收集付款方式并确认 SetupIntent；
7. 服务端监听成功事件并保存 PaymentMethod ID；
8. 后续创建支付时使用已验证的 Customer 和 PaymentMethod。

不要接受浏览器随意传入的 Customer ID 并在服务端直接创建 SetupIntent，否则可能让一个用户把付款方式绑定到其他人的客户记录。Client Secret 只应提供给当前流程的客户，不要写入公开日志、分析事件或工单截图；服务端仍要负责权限校验和业务状态更新。

## 客户同意与未来扣款说明

保存支付信息和未来扣款有合规与网络规则要求。商家应在保存时清楚告知客户：会保存什么付款方式、未来何时或如何使用、是否用于订阅续费，以及客户如何更新或移除付款方式。Stripe 的集成工具可以帮助收集同意，但商家仍需对符合适用法律、法规和卡网络规则负责。

建议在 UI 中区分：

- “保存此付款方式以便下次购买”；
- “用于当前订阅的定期续费”；
- “用于客户可能不在线时的后续扣款”；
- “仅用于当前这笔付款”。

不要把通用的“保存卡片”勾选框视为客户对任意未来收费的无限授权。保存方式、扣款时间、服务内容和取消途径应符合客户实际选择与商家条款。

## 支付方式 redisplay 与保存许可

Stripe PaymentMethod 可能包含 `allow_redisplay` 等信息，Checkout、Elements 和客户会话可用它判断付款方式是否适合再次显示给该客户。它与 SetupIntent 的 `usage` 作用不同：前者影响后续界面是否展示保存方式，后者说明未来扣款时客户可能是否在场。

使用 Payment Element 保存支付方式时，可以通过 Customer Session 配置是否显示保存同意框、是否展示已保存付款方式以及是否允许客户移除方式。若允许客户移除默认卡，要考虑仍有订阅依赖它的情况；删除后可能导致后续续费没有可用付款方式。删除前可以提示客户添加替代方式，或要求先确认其订阅状态。

不要因为付款方式已附加到 Customer 就默认可以在任何后续流程中重新展示或扣款。检查 Consent、`allow_redisplay` 和用途配置，并按照产品流程确认客户能够管理或删除付款方式。

## 认证、重定向和异步设置

部分支付方式在设置时可能要求客户完成认证、跳转到外部页面或验证银行账户。SetupIntent 的状态可能经历 `requires_payment_method`、`requires_confirmation`、`requires_action`、`processing` 等阶段，最终成功后才进入 `succeeded`。失败或客户关闭页面时，不应把付款方式标记为已设置。

若启用动态付款方式，检查该 SetupIntent 是否允许所需的重定向支付方式。Stripe 文档说明 redirect-based 方法可能需要 `return_url`，并且有些支付方式需要客户离开商家页面完成操作。前端应正确处理返回流程；服务端则通过 Webhook 确认最终状态。

如果SetupIntent等待银行账户微存款验证或其他后续步骤，系统需要将其状态记录为待完成，并向客户提供安全、清晰的验证入口。不要在验证未完成时就将该 PaymentMethod 设为可用于未来扣款。

## Webhook 更新而不是依赖前端返回页

客户可以关闭浏览器、手机应用或网络连接，因此 SetupIntent 的成功页面跳转不是可靠的唯一状态来源。服务器应监听 `setup_intent.succeeded`、`setup_intent.setup_failed` 等适用事件，验证签名、幂等处理并关联 Customer 和内部账户。

推荐处理逻辑：

- **成功：** 保存 PaymentMethod ID、Customer ID、用途和允许显示状态；
- **需要操作：** 保持设置为待处理，提示客户完成认证或验证；
- **失败：** 保存错误分类，允许客户更换方式或重新尝试；
- **取消：** 记录取消原因，不把方式标记为已可用；
- **重复事件：** 通过 Event ID 和 SetupIntent ID 避免重复创建默认方式或重复发送邮件。

未来实际扣款仍应有独立状态机。SetupIntent 成功只表示支付方式设置完成；之后的 PaymentIntent 或 Invoice 成功事件才表示实际扣款成功。把这两个状态混为一谈会导致客户尚未付款就被标记为已付费。

## 常见故障排查

### SetupIntent 成功，但付款方式没有出现在客户结账页

检查 SetupIntent 是否关联正确 Customer、PaymentMethod 是否已附加、`allow_redisplay` 是否符合该场景、Customer Session 是否启用了显示保存方式，以及当前页面是否使用相同 Stripe 账户和模式。

### 未来续费仍然需要客户认证

`off_session` 用途有助于为客户不在场的未来付款准备方式，但不能保证发卡行永远不会要求认证。监听 Invoice 付款失败或需要操作的相关事件，并通过邮件、Customer Portal 或安全恢复页面让客户回来完成付款。

### 保存卡片时要求进行验证

这通常是支付方式或发卡行要求的一部分。确认前端正确处理 `next_action` 和重定向返回，并在服务器端等到 SetupIntent 最终成功后才记录付款方式可用。

### 多个客户账户看到同一张卡

检查后端创建 SetupIntent 时 Customer ID 的来源、用户到 Stripe Customer 的映射和查询逻辑。不要仅凭电子邮箱匹配客户，也不要将前端传入的 Customer ID 作为授权依据。

### 客户删除付款方式后订阅续费失败

检查 Customer 的默认支付方式和所有关联 Subscription。若允许删除仍被订阅使用的方式，应同时提示客户添加替代支付方式，并在续费前监控付款方式是否可用。

## 测试清单

- 新客户通过 SetupIntent 保存付款方式并关联正确 Customer；
- 现有客户添加第二种付款方式；
- 分别测试 `on_session` 与 `off_session` 用途；
- 测试需要认证、重定向、取消、失败和异步完成的状态；
- Webhook 重复投递不会重复保存或通知；
- 前端超时后服务端能够查询现有 SetupIntent 状态；
- 付款方式只在客户同意的场景中展示；
- 客户移除订阅默认付款方式时有合理提示；
- SetupIntent 成功不会误触发付费履约；
- 后续 PaymentIntent/Invoice 失败后能引导客户恢复。

## 总结

Stripe SetupIntent 用于设置未来付款方式，而不是收取当前订单金额。创建时要关联正确 Customer，并依据真实业务选择 `on_session` 或 `off_session`。若客户当前正在付款并希望保存方式，也可以在 PaymentIntent 流程中按适用规则配置未来用途。

保存付款信息时需要清楚取得客户同意，并正确配置 redisplay 行为、认证、重定向和移除流程。通过 Webhook 更新 SetupIntent 的最终状态，将“支付方式设置成功”和“未来某笔付款成功”分开管理，能避免错误开通服务和无授权重复扣款。

## 官方资料

- [Stripe SetupIntent 使用指南](https://docs.stripe.com/payments/setup-intents)
- [Stripe 保存和复用付款方式](https://docs.stripe.com/payments/save-and-reuse)
- [Stripe SetupIntent 对象与 usage 字段](https://docs.stripe.com/api/setup_intents/object)
- [Stripe 创建 SetupIntent API](https://docs.stripe.com/api/setup_intents/create)
- [Stripe 事件类型参考](https://docs.stripe.com/api/events/types)
