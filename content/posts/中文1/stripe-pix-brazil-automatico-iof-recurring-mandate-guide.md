---
title: "Stripe Pix 与 Pix Automático：二维码付款、IOF 说明和循环扣款"
date: 2026-11-15
slug: "stripe-pix-brazil-automatico-iof-recurring-mandate-guide"
description: "Stripe Pix 如何处理巴西 BRL 二维码付款、跨境商户 IOF 展示、Pix Automático mandate、预扣通知等待期和异步续费状态。"
keywords:
  - Stripe Pix 支付
  - Pix Automático Stripe
  - Stripe Pix IOF
  - Pix recurring mandate
  - Stripe Pix 退款和争议
tags:
  - Pix
  - 巴西支付
---

Pix 是巴西中央银行开发的实时支付系统，客户可以在银行 App 中扫描二维码或粘贴 Pix 字符串来授权付款。Stripe Pix 既支持一次性付款，也支持 Pix Automático 循环付款。两种流程不能混为一谈：一次性 Pix 在客户现场批准后通常很快确认；Pix Automático 需要客户先在银行 App 批准 mandate，后续收费还要先发送预扣通知并等待规定时间，PaymentIntent 可能持续 processing。

跨境收款还涉及 IOF（巴西外汇交易税）展示和结算币种。Stripe 当前文档说明，向巴西客户收款的境外企业需要处理 IOF 如何由客户支付或由商家承担，并在 API 集成中提供相应披露。税率和规则可能变化，本文只按 Stripe 当前文档描述技术配置；上线前应核对 Stripe 最新说明并让财务或税务负责人确认实际口径。

## 谁可以收款，客户和币种怎么匹配

Pix 面向巴西客户，展示币种为 BRL。Stripe 支持多个国家的商户账户接收 Pix，但商户结算币种会根据账户所在国家而不同。巴西账户可用 BRL 结算；其他账户可能以 USD、EUR、GBP、CAD、AUD、SGD 等对应本地币种结算。客户位于巴西、账户资格、展示币种、跨境结算以及行业限制要分别核对。

Stripe 当前文档列出最低付款金额 0.50 BRL，默认单笔最高金额通常以 3,000 USD 等值 BRL 计算；账户经批准后可能有更高单笔上限。境外企业从巴西客户收款还有按客户和商户计算的日/月限制。循环扣款金额还必须落在客户批准的 mandate 范围内；超出授权金额时付款会失败。

商户资格可能受 MCC、行业政策和账户审核影响。启用前在 Dashboard 查看 Pix 状态及禁止、限制业务类别；不应因为网站支持 BRL 就默认账户已经有 Pix 能力。Connect direct charge 或使用 on_behalf_of 时，还需确认 connected account 所在国家、Pix activation 和 capability。

## 一次性 Pix：二维码、Pix 字符串和支付确认

一次性 Pix 的客户体验通常是：选择 Pix、查看二维码或 Pix 字符串、在自己的银行 App 中扫描或粘贴、确认金额并批准。客户不会一定被银行 App 自动带回商家网站，网页应保持结账状态，并由 Stripe SDK/组件在底层 PaymentIntent 到达终态后处理返回。客户批准流程的授权时长没有一个可对所有交易承诺的固定时限。

用 PaymentIntent 或 Checkout Session 保存内部订单号、BRL 价格和支付尝试标识。Webhook 验签、Event ID 去重、核对金额和币种后再履约。不要用客户手机上的“付款成功”截图直接把订单标为已收款，也不要只根据二维码已显示就发货。Checkout 返回页面后仍要检查 Intent 的最终状态。

Stripe 的合作方可能发送客户收据或提醒邮件。商家可以在 Dashboard 中管理 Pix 支付相关邮件；若关闭合作方邮件而改由自己发送收据，需要确保 IOF 行项目展示与商家承担方式匹配。Receipt、付款成功事件和银行流水是三个不同信息来源。

## Pix Automático：mandate 与后续扣款

Pix Automático 适用于符合条件的跨境商户，巴西本地注册的企业当前不能使用该自动扣款功能。客户在首次流程中通过银行 App 授权 mandate，确定金额与计费周期。创建 mandate 可使用 SetupIntent（不收首笔款）或 PaymentIntent（同时收取首笔款），具体集成按 Stripe Pix Automático 指南实现。结账页上的勾选框或文字同意不能代替客户在银行 App 完成授权。

后续自动收费必须遵守 mandate 的金额和周期；金额超过客户授权范围会失败。扣款前需要发送预扣通知，并等待至少三天后再提交收费；续费不是同步扣款，PaymentIntent 会处于 processing，带重试的确认可能最长到七天。账单系统应把“已排期”“预扣通知中”“处理中”“已成功”“失败”分开表示，不要在创建 Invoice 时就开通新周期权限。

保存 Charge 上的 Pix mandate ID，然后通过 Mandates API 查询授权详情。Mandate 对象通常不直接显示在 Dashboard，因此服务端保存授权 ID、amount、周期、状态和 expiration 信息，便于客户支持和审计。客户可以在银行 App 撤销授权，Stripe 会发送 mandate.updated；撤销后要停止后续收费，并要求客户重新授权后才能恢复自动扣款。

## IOF：向客户展示还是由商户承担

Stripe 当前文档说明，巴西客户向境外商户付款涉及 IOF。Stripe 和合作方会处理收取与汇缴，但商家仍要决定结账中如何呈现费用。Pix 参数 amount_includes_iof 可以控制商户是否承担该金额：默认行为下，客户在银行 App 看到交易加收的 IOF；商户选择承担时，Stripe 从商户结算款中扣除相应金额。

如果使用 Stripe Checkout 或 Elements，Stripe 会处理相应客户披露；直接 API 集成的商家需要根据配置显示适当说明。收据也建议列出 IOF。Stripe 文档当前列出 3.5% 的比率，但明确提示该比率可能由巴西主管机关调整。不要把文章中的税率硬编码进长期业务逻辑；上线前查看最新 Stripe 文档和账户显示，并由财务确认商家是否承担该费用。

## 退款、争议和银行账单识别

Stripe 当前 Pix 文档说明，退款可在原付款后 90 天内发起，支持全额和部分退款；客户通常几分钟内收到，但没有保证的最长完成时间，退款提交后不可取消。以 Refund 对象状态跟踪处理，并在未完成时核对 Stripe 和合作方状态；成功请求或早期状态更新不等于客户银行账户已入账。

Pix 争议只在有限情形下发生，例如欺诈或账户接管，由客户通过银行发起，可能涉及 Pix 特殊退款机制（MED）。Stripe 会通知商家，但商家不能通过 Stripe 提交证据抗辩，合作方的决定不能上诉。财务要把争议金额变动、退款和原付款记录关联，客服及时将客户诉求升级到相应处理渠道。

Pix 不支持自定义 statement descriptor。客户银行账单可能显示 Ebanx 作为收款方和账单描述，而商家名称在付款时的 identifier 字段展示。客服解释订单时，应提前说明客户可能看到的付款接收方，并保存 Pix reference、PaymentIntent、Charge 和内部订单号。

## 上线前验证清单

测试 BRL 一次性支付二维码/字符串、客户中途退出、退款全额与部分、Pix Automático 首次授权、预扣通知间隔、3 天等待、processing 持续数天、mandate 撤销和超额扣款失败。确认本地账户与境外账户能力不同；核对日/月交易限额、Connect capability、IOF 由客户还是商户承担、API 披露文案及收据金额拆分。

Pix 的快速授权适合一次性订单，但自动扣款的 mandate、通知和结算是更长的异步流程。把两种支付状态机分开，用 Stripe 事件驱动订单和发票，再核对退款与争议；IOF 则按账户和当前规则向客户准确说明，才能避免续费误扣、对账差异和税费投诉。

## 官方资料

- [Stripe：Pix 支付](https://docs.stripe.com/payments/pix)
- [Stripe：Pix Automático 集成](https://docs.stripe.com/payments/pix/pix-automatico)
- [Stripe API：Pix 付款参数](https://docs.stripe.com/api/payment_intents/create)
- [Stripe API：Mandate 对象](https://docs.stripe.com/api/mandates/object)
- [Stripe：Refund 对象](https://docs.stripe.com/api/refunds/object)
