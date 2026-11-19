---
title: "Stripe Connect Accounts v1 与 v2 指南：能力配置、客户账户和迁移"
date: 2026-11-19
slug: "stripe-connect-accounts-v1-v2-capabilities-migration-guide"
description: "比较 Stripe Connect Accounts v1 与 v2 的账户模型、merchant/customer/recipient 配置、API 兼容方式、响应 include 字段和渐进式迁移检查。"
keywords:
  - Stripe Accounts v2
  - Connect v1 迁移
  - Stripe 连接账户配置
  - customer_account
  - Connect API 账户能力
tags:
  - Stripe
  - Connect
  - Accounts v2
  - API 迁移
  - 平台开发
---

# Stripe Connect Accounts v1 与 v2 指南：能力、客户账户与迁移

Stripe Connect 平台使用 Account 对象代表连接账户。随着 Accounts v2 API 的推出，平台可以用更统一的身份模型管理不同账户，并通过配置为账户增加收款、付款或资金接收等功能。v1 与 v2 的对象结构、能力声明和部分 API 参数不同，现有平台不能只把请求路径从 v1 换成 v2，就认为迁移完成。

更稳妥的做法是先比较当前集成依赖、连接账户类型和资金责任，再决定新增账户采用哪种模型，或是否要逐步扩展已有对象。Stripe 说明，部分功能尚未直接支持 v2 Account，但某些 v1 endpoint 可以接受 v2 Account ID，并把更新应用到对应 v2 属性。兼容机制能帮助分阶段迁移，却不代表所有 API、Webhook 和 Dashboard 功能都已一致支持。

## 一、Accounts v1 和 v2 的核心区别

Accounts v1 主要用于管理 Connect 连接账户及支付能力。Accounts v2 使用 configurations 描述账户要承担的角色，例如 merchant、customer、recipient 或 money_manager。平台可以按需给一个 Account 增加配置，在已有身份数据基础上启用新功能；符合条件时，v2 也能统一表示连接账户和部分 Customer 使用场景。

这使得账户对象更像“统一主体 + 按角色启用能力”的模型。merchant 配置用于向客户收款；customer 配置可让平台向该账户收费或用于订阅、发票场景；recipient 配置用于接收资金转移；money_manager 配置支持金融账户资金管理。每种配置下还有具体 capability 和验证要求，不能只看到配置已创建就假设全部功能可用。

v1 和 v2 仍并行存在。平台要按所使用的具体 endpoint 和对象字段判断适用模型。API 响应、Webhook 事件结构和可扩展属性可能不同；若代码把 Account ID 当作只有一种固定 JSON 形状，迁移时容易出现字段为空、类型判断错误或 webhook consumer 无法解析。

## 二、能力配置不等于审批已经完成

Accounts v2 的配置表达账户需要哪些功能，但相应能力仍可能需要 Stripe 验证、收集更多资料或等待激活。创建 merchant 配置并请求 card payments，不表示账户可以立即收款；recipient 配置也不代表所有资金转移条件已经满足。平台应监听账户能力与要求状态，并让产品界面展示“待资料”“审核中”“可用”或“受限”等真实状态。

不同能力的 onboarding 要求不同。平台需要判断由 Stripe 还是平台自己收集资料、谁承担负余额或损失责任，以及连接账户能否使用 Stripe Dashboard。Accounts v2 的 defaults 等字段可能与 v1 controller properties 对应；这些责任设置会影响费用收取、损失处理和账户功能配置，属于业务与风险设计，不只是 API 语法。

建立数据库模型时，应保存账户对象 ID、配置类型、能力状态、资料要求和账户上下文。不要仅在用户资料中保存一个布尔值“Connect 已完成”。账户可能在未来增加 customer 或 recipient 能力，配置状态也可能变化，应依据 Stripe 服务端状态更新。

## 三、把 Connect Account 用作 Customer 的变化

Accounts v2 在部分请求中支持将配置为 customer 的 Account 用作传统 Customer 对象。Stripe 文档指出，一些接受 customer 参数的 API 也提供 customer_account 参数，可接收 v2 Account ID。这样平台在相应场景中可以使用统一 Account 身份，而不必对所有账户都额外维护 Customer 对象。

但 v1 API 集成不能把 Account ID 直接传给只接受 Customer ID 的端点。若既有平台使用 v1 并为连接账户创建订阅，通常仍需单独创建和管理 Customer 对象。迁移后要逐个检查 Checkout、SetupIntent、PaymentIntent、Subscription、Invoice、Customer Portal 及事件处理的账户关联方式；不能只修改 create customer 的位置。

如平台同时服务卖家与买家，一个 Account 可能承担多个配置角色，但 UI、权限和账务仍要区分角色。一个连接账户作为商户收款，另一个场景作为客户被收费，不能因此共用未经区分的业务资料或默认支付方式。为每种用户旅程记录应该使用 merchant Account、customer Account 还是 Customer 对象，避免把一个主体错误关联到另一个交易。

## 四、响应字段 include 与数据读取

Accounts v2 默认响应中，部分属性可能返回 null，即使该属性在对象中实际存在。Stripe 文档要求通过 include 参数请求需要读取的属性。迁移时如果代码把响应中的 null 一律理解为“没有值”，可能导致误判账户没有配置、没有身份信息或没有要求状态。

设计请求封装层时，将业务所需字段放入显式 include 列表，并为 API 版本变化建立测试。不要在每个页面临时拼接 include 参数，否则不同服务可能读取到不一致的 Account 数据。记录当前 API version，按官方文档核对字段何时返回以及版本要求。

Webhook 中的 Account 对象也应采用适合该事件/API 版本的解析逻辑。不要假定 API GET 的响应字段与历史事件 payload 完全一致。收到事件后可按事件内的 object ID 查询最新状态，但需要依据账户上下文和权限正确发起请求。

## 五、渐进式迁移方法

迁移前先盘点代码和数据：

1. 列出创建、更新、读取 Account 的所有 endpoint。
2. 找出依赖 v1 controller、capabilities、requirements 和 payout 字段的逻辑。
3. 标记依赖 Customer ID 的 Checkout、订阅、发票和付款请求。
4. 梳理 Connect 账户类型、Dashboard 类型、资金流和损失责任。
5. 确认目标 v2 configurations、capabilities 和每种账户资料要求。
6. 选择一个 Sandbox 测试账户类型，先跑通开户、收款、退款、转账和事件处理。
7. 对部分请求使用 v2 Account ID 兼容的 v1 endpoint 时，验证字段更新落在预期对象。
8. 分阶段上线，对新账户与既有账户明确采用的对象模型。
9. 监控能力状态、Webhook 错误、Customer 关联错误和付款失败。
10. 记录回滚方案以及出现重复 Customer 或账户 ID 关联异常时的修复步骤。

账户模型迁移可能影响税表、账户管理、资金移动、Dashboard 嵌入组件和财务对账，不应只覆盖开户流程。平台应在 staging 使用代表性的 connected account type 和典型国家测试；实际资格和数据迁移方案应向 Stripe 确认。

## 六、常见问题

**v2 Account 返回某字段为 null。** 检查该字段是否需要通过 include 请求，而不是立刻判断账户未设置该资料。

**某个 v1 API 能接受 v2 Account ID，是否代表 v2 全面支持？** 不是。只有适用的 v1 endpoints 会按文档处理 v2 Account ID，其他功能仍需确认直接支持情况。

**customer_account 参数报错。** 确认目标 API 是否提供该参数，账户是否具备 customer 配置，以及调用的 API 版本和对象 ID 是否正确。

**新增配置后能力仍不可用。** 检查相关资料要求和 capability 状态。配置是功能角色的声明，不等于验证已经完成。

**升级后 webhook 事件解析失败。** 检查事件对象类型、API 版本、账户上下文和 include 规则，避免复用只适配 v1 结构的解析器。

## 七、上线检查清单

- 明确哪些账户仍使用 v1，哪些新流程计划采用 v2。
- 将每项业务功能映射到对应 configuration 和 capability。
- 复核费用收取、负余额、损失责任和 Dashboard 配置。
- 为需要的 v2 响应字段显式设置 include。
- 确认 customer_account 和 Customer 的使用边界。
- 将账户能力、资料要求和功能状态存入可审计的数据模型。
- 在 Sandbox 测试开户、收款、付款、退款、Webhook 和 Connect 上下文。
- 对 API 版本和事件格式做兼容测试。
- 分批发布并监控账户状态和支付数据。
- 对不明确的账户迁移和兼容 endpoint 向 Stripe 获取确认。

## 总结

Accounts v2 通过 configurations 让账户以统一身份承担不同角色，适合需要灵活组合收款、付款和资金管理能力的平台。Accounts v1 与 v2 在账户模型、能力表达、Customer 参数和响应字段方面存在差异，兼容 endpoint 只能帮助部分功能渐进过渡。

迁移的关键是建立业务到 configuration/capability 的映射，检查 Customer 依赖、API 响应 include、Webhook 结构、账户上下文和责任配置。先在 Sandbox 验证完整资金流，再按账户类型逐步迁移，并依据 Stripe 当前 API 文档确认预览状态和资格范围。

## 官方参考资料

- [Stripe Connect 与 Accounts v2](https://docs.stripe.com/connect/accounts-v2)
- [Accounts v2 连接账户配置](https://docs.stripe.com/connect/accounts-v2/connected-account-configuration)
- [Stripe API include 响应值](https://docs.stripe.com/api-v2-overview#include)
- [使用 Accounts v2 的客户付款](https://docs.stripe.com/payments/existing-customers)
