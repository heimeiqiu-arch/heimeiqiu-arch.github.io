---
title: "Stripe Connect 连接账户付款方式管理：配置继承、商户身份与能力状态"
date: 2026-11-19
slug: stripe-connect-connected-account-payment-methods-guide
description: "讲解 Stripe Connect 平台如何管理 connected accounts 的付款方式：charge type 与 merchant of record 的关系、平台默认配置、账户覆盖、capability 要求和资格排查。"
keywords:
  - Stripe Connect 付款方式管理
  - connected account payment methods
  - Stripe Connect Payment Method Configurations
  - Stripe Connect merchant of record
  - Stripe connected account capability
  - Connect 支付方式不显示
tags:
  - Stripe
  - Stripe Connect
  - Payment Methods
  - Connected Accounts
---

Connect 平台可能同时服务多个卖家，每个连接账户的国家、业务类别、验证状态和可用付款方式都可能不同。若平台在 Checkout 或 Payment Element 中明确指定了某种付款方式，但它没有在客户页面显示，原因不一定是前端渲染错误，也可能是该方式没有在正确的 Stripe 账户配置中启用，或者 connected account 尚未满足对应 capability 要求。

Stripe Connect 付款方式管理需要结合 charge type 和 merchant of record（MoR，记录商户）判断。Direct charge、间接收费且设置 on_behalf_of、以及平台自己作为 MoR 的间接收费，所需的付款方式配置位置不同。本文讲解默认配置如何继承、平台与连接账户如何分工、如何查看账户资格和 capability 状态，以及发布配置变更前应如何检查潜在影响。

## 先确定款项对应的记录商户

Stripe 文档按照记录商户和 charge type 区分支付方式配置：

- **Direct charges：** 客户直接与 connected account 交易，付款方式需要在 connected account 所属的配置中启用。
- **间接收费并设置 on_behalf_of：** connected account 被指定为记录商户，付款方式同样需要在该 connected account 可用。
- **平台作为记录商户的间接收费：** 如果没有设置 on_behalf_of，通常应在平台账户的配置中启用付款方式；连接账户已启用哪些方式并不决定这类支付能否使用。

因此，排查前先查支付对象的创建账户和 on_behalf_of 设置，而不是直接在所有账户里打开该付款方式。创建 PaymentIntent、Checkout Session 或其他支付对象时，若集成明确指定 payment_method_types，也要确认这些方式在对应的 MoR 账户上启用且适用于当前交易。

Stripe 推荐在适用场景使用 Dynamic payment methods，由 Stripe 根据付款对象、账户、地区、币种和支付流程动态决定可显示的付款方式。它可以减少平台手工维护固定列表，但不能绕过账户资格、国家限制和 capability 要求。

## 平台默认配置与账户继承

平台可以在 Dashboard 的 Connect 付款方式设置中为 connected accounts 配置默认付款方式。配置页包含“连接账户”和“平台账户”两组设置。连接账户配置适用于 Direct charges 和设置 on_behalf_of 的间接收费；平台账户配置适用于平台作为记录商户的间接收费，以及与 Connect 无关的普通平台支付。

每组配置都有默认 configuration。没有为某笔交易指定其他 configuration 时，使用默认配置。平台也可以创建额外配置，例如订阅支付配置、大额支付配置或业务场景配置，并在适用 API 流程中为交易选择对应配置。创建多份配置前要设计命名和作用范围，否则排查“为什么这笔付款看不到某个方式”时，很难判断实际使用哪份配置。

连接账户配置允许对支付方式设置 On by default、Off by default 或 Blocked 等状态。On by default 表示符合资格且仍继承平台默认的账户可以使用；Off by default 表示默认不启用，但拥有完整 Dashboard 或相应自助设置权限的连接账户可能可以自行打开；Blocked 则由平台禁止，连接账户不能自行开启。某些付款方式需由账户单独配置，会显示为 per-account 设置。

若支付方式支持国家维度默认值，可以对不同国家分别设定状态。修改主默认设置时，可能同时影响国家默认值。平台应在保存前检查国家覆盖和账户例外，避免原本只想调整一个市场，却改变所有市场的配置。

## 账户覆盖、商家自助与平台管控

连接账户如果拥有完整 Stripe Dashboard，或平台为其提供 Payment method settings 嵌入式组件，可以在平台允许的范围内管理自己的付款方式。管理员可以通过 configuration 的 Account customization 选择是否允许 connected accounts 自行配置；已被平台标记为 Blocked 的方式通常不能被账户自行开启。

不是每个 connected account 都需要同样的支付方式。平台可以在统一默认值基础上，对单独账户取消继承并设置覆盖。Dashboard 中的账户详情页可以检查某个方式是否继承平台设置、当前状态以及是否允许启用。若账户自行设置了 On 或 Off，后续修改平台默认状态不一定覆盖这些明确选择；平台更改默认值主要影响仍使用默认继承的账户。

如果平台在所有账户层级都强制覆盖，可能限制卖家选择符合本地客户习惯的方式；如果完全开放自助，则可能出现卖家打开了自己没有资格或尚未完成审核的方式。应定义平台设置、账户自助和单账户例外三者的优先级，并在卖家后台用清晰标签显示来源：平台默认、账户自选或平台强制禁用。

## Eligibility 与 capability 排查

账户未启用某种付款方式可能是资格问题。Stripe 文档列出一些原因：账户没有完成该付款方式 capability 所需验证信息；该方式禁止账户所使用的 MCC；账户仅为收款人或资金接收方而不接受付款；Stripe 对账户风险采取限制等。

Dashboard 配置页可按状态查看账户统计，如 Missing info、Ineligible、Eligible 和 Enabled。Missing info 表示账户仍有未满足的要求；Ineligible 表示账户不满足国家、MCC 或其他资格条件；Eligible 表示账户符合资格但尚未启用；Enabled 表示符合资格且已经启用。对有对应 capability 的支付方式，界面可能显示 capability 状态而非普通 Enabled 标识。

启用某个支付方式和请求其 capability 是关联但不同的步骤。Stripe 文档说明，多数付款方式有相关 capability，需要先激活后账户才能接受该方式。如果平台将付款方式设为默认开启，Stripe 可能为符合资格且已完成要求的连接账户自动请求 capability；若账户缺少信息，可能出现需要补件或受限状态。计划全局开通前，应先了解这类自动请求会如何影响存量账户。

检查 API 时，要区分 v1 与 v2 Account 对象字段结构。v1 可以检索 Account 的 capabilities；v2 则读取 merchant configuration 下的 capabilities，并可通过更新请求设置 requested。请求成功不代表 capability 立即 active，Stripe 可能还需要时间或额外信息。应监控能力状态及 requirements，而不是仅看 API 是否返回 200。

## 变更会影响多少账户

Connected accounts 的 Payment Method Configuration 主要通过 Dashboard 管理。Stripe 文档指出，修改平台连接账户配置可能影响多个 connected accounts，保存变更前会要求确认。因此，将原本 Off by default 改成 On by default，不应当当作一个无影响的展示设置；可能涉及大量账户资格检查、capability 请求和真实交易可用性改变。

建议分阶段管理配置：先统计国家、账户类型、MCC 和 capability 状态；对少量内部测试账户验证 PaymentIntent 或 Checkout 页面；观察付款方式实际显示和授权结果；再按国家或账户群体逐步扩大。变更后监控 Missing info、Ineligible、capability pending 和支付失败支持工单，准备在必要时恢复平台默认值。

导出的 eligible account CSV 也有范围限制。Stripe 文档说明，下载的账户清单可能不包含最近 90 天没有支付活动的账户，除非该账户创建时间少于 30 天。不能把下载文件当成完整所有账户名册。发布配置前应结合自己的 Connect 账户数据库和 Dashboard 汇总统计进行核对。

## 常见排查步骤

**客户页面没有显示某付款方式：** 确认 Payment Element 或 Checkout 使用 Dynamic payment methods 还是固定指定方式；确认 charge type 与 MoR；核对平台或 connected account 上对应配置和该账户的实际覆盖。

**API 明确指定了方式但创建失败：** 确认支付方式是否在正确的账户启用、币种和国家是否支持、支付对象是否使用正确 Stripe account context，以及是否缺少 capability。

**账户页面显示 Missing info：** 通过 Dashboard 或 API 查看该 capability 的 outstanding requirements，提示 connected account 完成相关验证信息。等待 Stripe 处理后再次检查能力状态，不要循环重复请求。

**账户标记 Ineligible：** 检查 MCC、国家、账户是否具有收款能力，以及是否存在 Stripe 风险限制。平台不能仅凭自身设置强行开启不具备资格的付款方式。

**平台默认值变化没有影响某些账户：** 检查账户是否显式覆盖了该方式状态，而非继续继承 platform default。只调整未覆盖账户的默认值不会覆盖已有的明确账户选择。

## 上线前检查清单

- 根据 Direct、Destination、Separate charges and transfers 和 on_behalf_of 确定记录商户与付款方式配置位置。
- 优先评估 Dynamic payment methods，并确认当前支付流程支持的 Payment Method Configuration。
- 先在测试环境和少数 connected accounts 验证页面展示及 capability 状态。
- 检查国家默认设置、MCC 适用性、账户类型和所需验证信息。
- 确认是否允许 connected accounts 自行管理，哪些方式被平台强制 Blocked。
- 在批量修改配置前，导出账户状态并了解 CSV 统计范围。
- 发布后监控 capability 申请、Missing info、Ineligible、交易展示和客服问题。

## 常见问题

### 为什么平台把支付方式设为 On，某些账户仍无法使用？

On by default 只对符合资格且采用平台默认设置的账户生效。账户可能缺少验证信息、不支持该国家或 MCC，或者已有单独覆盖。必要 capability 也可能尚未激活。

### 连接账户可以自己开启付款方式吗？

取决于平台是否允许账户管理、账户是否具备完整 Dashboard 或嵌入式支付方式设置能力，以及平台有没有将该方式标记为 Blocked。需要为账户配置明确权限。

### 选择付款方式配置时需要看 charge type 吗？

需要。Direct charge 和将 connected account 设为 MoR 的间接收费通常需要在 connected account 配置中启用；平台作为 MoR 的间接收费则通常由平台配置决定。

### 请求 capability 后为什么还不是 active？

Stripe 可能需要处理申请或要求补充信息。API 请求成功并不代表 capability 已立即激活，要继续查看 capability 状态和 requirements。

## 总结

Stripe Connect 付款方式配置取决于记录商户和资金流。正确做法是先识别 charge type 与 on_behalf_of，再确定应在哪个配置组启用方式，最后检查 connected account 的资格、国家、MCC 和 capability 状态。

平台默认值、账户自助和单账户覆盖需要有明确的优先级。全局更改可能触及多个连接账户和 capability 请求，上线前应先测试、统计影响范围并准备回滚。更多细节请查看 [Stripe Connect connected account 付款方式管理](https://docs.stripe.com/connect/manage-payment-methods)、[Connect 收费类型](https://docs.stripe.com/connect/charges) 和 [Connect capability 指南](https://docs.stripe.com/connect/account-capabilities)。
