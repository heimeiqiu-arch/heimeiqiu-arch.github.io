---
title: "Stripe request_three_d_secure 指南：automatic、any 与 challenge 选择"
date: 2026-11-15
slug: "stripe-request-three-d-secure-automatic-any-challenge-guide"
description: "解释 Stripe request_three_d_secure 的 automatic、any 和 challenge 选项，及其与 SCA Engine、Radar、发卡行决策和支付转化的关系。"
keywords:
  - request_three_d_secure
  - Stripe 3DS automatic any challenge
  - Stripe 手动请求 3D Secure
  - Stripe Radar SCA Engine
  - PaymentIntent 3DS 设置
tags:
  - Stripe
  - 3D Secure
  - Radar
  - PaymentIntent
---

Stripe 的 request_three_d_secure 参数可用于设置银行卡付款中 3D Secure 的请求偏好。常见取值为 automatic、any 和 challenge。很多商家看到参数中有 challenge，就以为可以完全控制客户是否弹出验证；实际上，这些值是向 Stripe 和支付网络表达偏好，最终的认证流程还会受到发卡行、卡片能力和交易规则影响。

Stripe 建议大多数集成依靠 SCA Engine，根据风险和监管要求自动决定是否提示客户认证。只有当商家的风控系统有清晰、经验证的策略时，才考虑手动请求 3DS。配置前要确认采用的是 PaymentIntent、订阅付款设置、Invoice 还是 SetupIntent，并检查相应接口是否提供该参数。参数设置不能替代支付状态处理、客户授权或失败后的恢复流程。

## 三种取值代表什么

automatic 是默认选项，Stripe SCA Engine 根据风险级别及其他要求自动提示认证。对于多数在线商家，这是更稳妥的起点：Stripe 会结合交易上下文处理认证需求，减少商家自行维护大量国家、发卡行和风险规则的工作。

any 表示商家希望发起 3DS 请求，并倾向于 frictionless 流程。Frictionless 是银行在后台完成认证评估、客户可能不需要手动输入验证码或确认的路径。但不能保证每笔交易都会按预期走 frictionless，也不能保证一定不需要客户操作；发卡行决定最终认证体验。

challenge 表示希望请求需要客户主动参与的 3DS 挑战流程，例如银行页面上的确认、一次性验证码或生物识别。该参数表达的是 challenge 偏好，不是强制所有发卡行必须显示挑战，也不能保证客户所在设备和银行均支持相同交互。Stripe 文档明确说明，issuer 决定最终认证流程，Stripe 无法保证请求偏好一定实现。

## 什么时候适合手动请求

商家若有自有风控系统，并已通过可解释的交易特征评估何时请求额外认证，可以将其决策映射到参数。策略应基于合法、透明、经过测试的信号，监控认证成功率、支付授权率、转化率和欺诈结果，而不是对所有交易盲目要求挑战。

某些企业出于风险控制或责任转移考虑，可能希望更频繁地尝试 3DS。但认证增加也会让客户离开页面、遇到银行系统错误或放弃付款。应先在测试环境验证 PaymentIntent 状态流程，再用小流量观察实际交易结果。测试要区分 frictionless、challenge 成功、客户取消、认证超时、发卡行不支持等情况。

如果没有自有风控策略，仅为“保险”而全局设置 challenge，可能徒增结账摩擦。另一方面，也不要为提高表面授权率而关闭或绕过法律或银行要求的强客户认证。正确处理方式是让 Stripe SCA Engine 和支付网络在实际交易中决定认证要求，并为需要动作的客户提供可用的前端流程。

## 与 Radar 和 Stripe SCA Engine 的关系

SCA Engine 是自动判断认证需求的重要组成部分。request_three_d_secure 的手动值会影响 3DS 请求偏好，但不应把它理解成“关闭 Radar”或“完全覆盖银行规则”。若商家使用 Radar 风控规则，应记录某类规则是否影响 3DS 请求、是否与 SCA 自动认证策略冲突，并通过实际交易数据验证。

同一个支付请求还会受到金额、国家、卡组织、客户所在地、业务类型和支付方式等因素影响。不能仅根据一次测试卡行为推断所有地区都一样。账户 API 版本和集成产品不同，参数的放置层级也可能不同；订阅可通过 subscription payment_settings，PaymentIntent 和 SetupIntent 在相应的 payment_method_options.card 下配置。以当前使用的 Stripe API 文档和 SDK 为准，不要将某个产品参数路径照搬到另一对象上。

若使用 Checkout Session，支付由 Checkout 管理，商家可传递适用的 PaymentIntent 创建参数，但要确认当前 Checkout 模式是否支持预期设置。若是 Stripe Billing 自动生成的续费 PaymentIntent，应在订阅或发票支付设置层配置，不要只改网站初次结账的 PaymentIntent，却忽略后续账单。

## 需要客户认证时的状态处理

当付款需要客户参与 3DS 时，PaymentIntent 可能要求额外动作。前端应使用 Stripe.js 或 Payment Element 根据 PaymentIntent 的客户端状态继续认证，并在完成后让服务端核实最终状态。不要以点击了“支付”或浏览器跳转到 success_url 为依据就发货。

如果银行拒绝、认证失败或客户取消，订单应保留失败原因和 PaymentIntent ID，并向客户提供安全的重新付款或更换卡片入口。重试时先检查旧 PaymentIntent 当前状态，避免在旧支付仍可能成功时创建重复扣款。后端 webhook 也要验证签名并去重，确保 PaymentIntent 成功事件不会重复开通权益。

订阅场景还要区分一次性支付认证和后续离线续费。客户首笔付款成功并不保证每次续费都无需认证；后续发票可能处于需要客户动作或付款失败状态。商家应根据 Invoice 和 PaymentIntent 状态引导客户回到 Billing Portal 或补款页面。

## 测试和指标设计

测试应覆盖自动认证、要求 3DS、需要客户挑战以及认证取消的场景。Stripe 提供测试 PaymentMethod 来模拟认证所需的支付行为；通过 Stripe CLI 转发相关 webhook，验证数据库状态、客户页面、订单履约和重复事件处理。不要只确认 API 接受了 request_three_d_secure 字段，就认为生产支付一定会显示挑战。

上线监控可按国家、支付方式、发卡行响应、交易金额和参数取值观察：3DS 请求率、挑战完成率、认证失败率、支付授权率、放弃率和欺诈争议。将设置从 automatic 改成 any 或 challenge 之前，先建立基准；比较时关注实际授权和欺诈结果，而不只看是否出现 3DS 页面。必要时按风险规则或交易类型分层，而非全局强制。

## 常见误区

**把 challenge 当成强制弹窗。** 参数只表达偏好，发卡行决定实际认证流程。

**认为 any 就完全无感。** any 倾向 frictionless，但银行仍可能要求客户主动验证。

**在没有策略时全局强制挑战。** 认证摩擦可能降低付款完成率，需根据风险和转化数据评估。

**以为 automatic 等于不做认证。** SCA Engine 会按监管及风险情况自动提示需要的认证。

**只在初次付款设置 3DS。** 订阅续费和后续付款可能由不同的 Invoice 或 Subscription 参数控制。

**认证页面完成就立即当作已付款。** 需要服务端核实 PaymentIntent 和订单状态，再履约。

## 上线检查清单

- 默认优先评估使用 automatic 与 SCA Engine；
- 只有在有自有风控策略时才手动设定偏好；
- 确认参数设置在正确的 PaymentIntent、Subscription 或 SetupIntent 层级；
- Checkout 与 Billing 的首付款和续费路径都已检查；
- 对 frictionless、challenge、取消和失败进行完整测试；
- PaymentIntent 需要动作时提供安全的客户认证入口；
- 认证后由服务端及 webhook 核验最终付款；
- 对重试实施幂等，防止同一账单重复扣款；
- 监控认证完成率、支付授权率和争议结果；
- API 版本或参数更新前阅读当前官方文档。

## 总结

request_three_d_secure 支持 automatic、any 和 challenge 三种常见偏好。automatic 让 Stripe SCA Engine 按风险和法规自动处理；any 请求 3DS 并倾向 frictionless；challenge 请求客户主动参与的验证偏好。但最终流程由发卡行和交易条件决定，商家不能把这些选项视作确定性开关。

默认使用自动策略通常更简单。若使用手动请求，应结合自有风险分析、支付转化和认证结果持续评估。无论采用哪种设置，都要在认证所需时正确处理 PaymentIntent 状态、客户返回、Webhook 幂等和订单履约。

## 参考资料

- [Stripe：3D Secure 认证](https://docs.stripe.com/payments/3d-secure)
- [Stripe API：PaymentIntent 对象](https://docs.stripe.com/api/payment_intents/object)
- [Stripe API：SetupIntent 对象](https://docs.stripe.com/api/setup_intents/object)
- [Stripe API：更新 Subscription](https://docs.stripe.com/api/subscriptions/update)
