---
title: "Stripe PayPal 收款实战：结算偏好、授权、退款和争议对账"
date: 2026-11-15
slug: "stripe-paypal-settlement-preference-mandate-refund-dispute-guide"
description: "通过 Stripe 接入 PayPal 时，如何检查欧洲商户资格、选择 Stripe 或 PayPal 结算、管理循环扣款 mandate、追踪退款和提交争议证据。"
keywords:
  - Stripe PayPal 收款
  - Stripe PayPal settlement preference
  - PayPal mandate Stripe
  - Stripe PayPal 退款
  - PayPal dispute Stripe
tags:
  - Stripe
  - PayPal
  - 钱包支付
---

Stripe 可以在受支持的欧洲国家为商户处理 PayPal 付款。客户通过 PayPal 授权后，选择余额、关联银行卡或银行账户等资金来源完成支付。虽然客户看到的是 PayPal 登录和授权页面，但款项的结算路径可能涉及 Stripe 余额或 PayPal 账户，进而影响退款资金来源、争议金额管理和财务报表。把“接入 PayPal”误当成所有地区都可用，或没有确认结算偏好就编写退款流程，容易造成对账差异。

本文说明通过 Stripe 接入 PayPal 的账户资格、跳转付款、未来付款授权、退款、争议和 Connect 边界。支付方式的可用国家、商户政策和功能可能变化；以 Stripe Dashboard、PayPal 的账户状态和官方最新文档为准。

## 先确认是 Stripe PayPal 还是自定义 PayPal

本文讨论的是 Stripe 自身支持的 PayPal 支付方式，适用于 Stripe 文档列出的受支持欧洲商户国家。若企业 Stripe 账户位于其他国家，或希望直接使用自己的 PayPal 商户账户，可能需要评估 Stripe 的 custom payment method 集成，而不能直接照搬此处的 API 和结算流程。

客户可以在全球多地使用 PayPal，但商户账户的国家资格仍然受限。账户所在国家、展示币种、商品类别、PayPal 商户政策和审核状态都可能影响支付方式是否启用。不要仅凭消费者能够拥有 PayPal 账户就假设你的 Stripe Dashboard 会显示 PayPal。先启用支付方式并在测试模式确认 Checkout、Payment Element 和正式环境配置。

## 客户授权和订单确认

Checkout 流程中，客户选择 PayPal 后跳转到 PayPal 托管页面，登录、选择资金来源并批准付款，之后返回商家网站。Stripe 通常会立即报告成功或失败，但服务端仍应从 Stripe PaymentIntent 或 Checkout Session 确认，并通过签名验证的 Webhook 更新订单。浏览器返回页面用于展示体验，不能独自决定订单已付款。

把内部订单主键关联到 Checkout Session 或 PaymentIntent，保存 PayPal transaction ID、付款金额、币种和 Customer。Webhook 处理需要 Event ID 去重并对履约动作设置幂等，避免 Stripe 重试或客户刷新页面导致重复发货。对于 PayPal 未授权、客户取消或支付失败的情况，订单保持失败或待付款，并引导客户安全重新尝试。

PayPal 支持手动捕获、部分捕获、全额与部分退款，但不是所有银行卡授权能力都适用。若采用授权后延迟捕获，测试授权到期、部分捕获金额和最终付款状态；不要将多次捕获或超额捕获能力推定为已支持。应以当前 Stripe PayPal 资料中的 capability 清单为准。

## 结算偏好决定钱在哪里

Stripe PayPal 集成可以涉及不同结算偏好：PayPal 资金可能结算到 Stripe，或结算到 PayPal。实际可用方式和账户配置应在 Stripe 与 PayPal 设置中核实。这个选择会改变退款资金来自哪里：若资金结算到 Stripe，退款从 Stripe 账户可用资金中扣除；若结算到 PayPal，则退款由 PayPal 账户余额或该账户可用资金来源承担。

争议金额的暂扣或管理位置也会随结算偏好变化。结算到 Stripe 时，相关款项会影响 Stripe 余额；结算到 PayPal 时，资金和争议过程可能需要在 PayPal 账户中管理。平台财务和客服应在内部付款记录中标明结算偏好，不然同一个 Stripe 报表看不到全部 PayPal 余额变动时，容易把差异误认为资金丢失。

PayPal 费用会出现在 Stripe Balance 和 Balance Activity 报表的费用部分，但 Stripe 税务发票中不一定包含 PayPal 费用文件；PayPal 可能在自己的 Dashboard 提供费用文件。财务对账要同时核对 Stripe 余额报表、Stripe payout、PayPal 账户流水以及适用的费用文档。

## 循环扣款 mandate 与撤销

保存 PayPal PaymentMethod 供未来付款需要客户授权 mandate。PayPal 托管授权流程并记录客户对未来付款的同意；循环支付还需要 PayPal 单独批准。上线前确认 PayPal 账户的 recurring payments 功能已启用且获准，不能只在 Stripe 侧创建了一个 PaymentMethod 就开始后台扣款。

Stripe Mandate 对象可以通过 API 查询，PayPal billing agreement ID（BAID）位于 mandate 的相关 PayPal 详情中。受限 API Key 如果要读取 mandate，需要具备相应权限。后台记录 Customer、PaymentMethod、Mandate ID 和授权状态；不要记录或处理客户 PayPal 密码。

如果客户在 PayPal 中撤销授权，Stripe 会撤销关联 Mandate 并发送 mandate.updated 事件。系统应验签、幂等处理并停止后续 off-session 扣款。商家也可以 detach 已保存的 PaymentMethod 停止未来使用。订阅取消、付款方式解绑和 PayPal 授权撤销是不同动作，内部状态机需要分别更新，避免客户撤销授权后订阅仍持续尝试扣款。

## 退款与资金来源

Stripe PayPal 付款通常可在原交易后 180 天内发起全额或部分退款。提交后不能取消；最终处理时间因买家资金来源而异，Stripe 无法保证固定完成时间。创建 Refund 后，读取其状态并监听 refund.updated 或 refund.failed。API 请求成功只代表退款已提交处理，不能直接通知客户“已经到账”。

退款资金来源取决于结算偏好。若失败，Refund 对象变为 failed，商家需要通过其他方式退款；此时确认相关款项返回 Stripe 还是仍由 PayPal 管理，再进行替代付款。替代退款要保留原付款、Refund ID、失败原因、审批人和支付凭证，避免原退款仍在处理时又重复给客户付款。

## PayPal 争议和证据提交

PayPal 支付可以出现争议，包括未收到商品或商品与描述不符等问题。同一笔 PayPal 付款可能出现多次争议；每个争议都需要独立处理，也分别影响争议指标。争议创建后，Stripe 会通过邮件、Dashboard 和 charge.dispute.created 事件通知商家，并提供 Dispute 的 due_by 截止时间。

不同争议类别的回复期限不同，Stripe 文档提示常见范围约为 2 至 19 个日历日；个案一律按 Dashboard 或 Dispute.evidence_details.due_by 处理。Stripe 对每个 PayPal dispute 只支持一次证据提交，因此要先收集订单、物流、交付、客户沟通和退款证据，再完成提交。部分争议类型如需额外沟通或申诉，Stripe Dashboard 不一定提供操作，需查看 PayPal Dashboard 是否有可用选项。

争议结算的资金处理也依结算偏好而不同。按争议独立保存付款、争议对象、证据提交和裁决状态，不要把同一笔订单的多个争议合并成一个记录。监控事件重复与超期，确保客服能够在截止日前提供完整证据。

## Connect 平台限制

PayPal 在 Connect 上只适用于获准的在线市场类型：平台收取客户付款，再向子账户或服务提供者付款。它不适用于所有“让商户直接接收付款”的平台模式。Stripe 文档当前说明 PayPal 支持 destination charges 和 separate charges and transfers，但不支持 direct charges 或 on_behalf_of；平台需在申请前确认自身 Connect 业务模型符合条件。

交易模型会影响商户展示、资金结算、争议管理和退款对象。开发时在测试账户验证平台、connected account、资金转移与 payout 关系，并在产品中说明谁是交易责任方。不要在 production 才发现平台账户类型不被批准。

## 上线检查清单

确认 Stripe 商户国家支持 PayPal、账户与 PayPal 商户政策允许该业务、结算偏好已确定、支持币种已测试。覆盖客户授权成功与取消、Webhook 重试、手动与部分捕获、循环 mandate 建立及撤销、全额与部分退款、退款失败、争议证据提交和 Connect charge 类型。把 Stripe 余额、PayPal 余额与费用文档纳入财务月结。

通过 Stripe 接入 PayPal 不只是加一个钱包按钮。商户资格、授权 mandate、结算偏好和争议位置都会影响运营流程。先确定资金落点，再分别管理付款、退款与争议对象，才能给客户可靠的确认并让财务对上每一笔资金。

## 官方资料

- [Stripe：PayPal 支付](https://docs.stripe.com/payments/paypal)
- [Stripe：选择 PayPal 结算偏好](https://docs.stripe.com/payments/paypal/choose-settlement-preference)
- [Stripe：设置 PayPal 未来付款](https://docs.stripe.com/payments/paypal/set-up-future-payments)
- [Stripe：PayPal 争议处理](https://docs.stripe.com/payments/paypal)
- [Stripe API：Mandate 对象](https://docs.stripe.com/api/mandates/retrieve)
