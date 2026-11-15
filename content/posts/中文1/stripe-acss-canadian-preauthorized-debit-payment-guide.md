---
title: "Stripe 加拿大预授权借记 ACSS：账户验证、延迟付款和争议退款"
date: 2026-11-15
description: "介绍 Stripe ACSS/PAD 的加拿大账户验证、CAD 与 USD 币种匹配、mandate 规则、最长 5 个工作日确认以及退款双重入账风险。"
slug: "stripe-acss-canadian-preauthorized-debit-payment-guide"
tags: ["Stripe", "ACSS", "加拿大预授权借记", "银行付款"]
keywords: ["Stripe ACSS Direct Debit", "加拿大预授权借记 Stripe", "PAD mandate", "ACSS 付款延迟", "ACSS 退款争议"]
---

# Stripe 加拿大预授权借记 ACSS：账户验证、延迟付款和争议退款

Stripe 的 Canadian pre-authorized debit（PAD）通过加拿大的 Automated Clearing Settlement System（ACSS）从客户银行账户扣款，适用于加拿大客户的银行借记付款。它可以用于一次性和定期扣款，但付款确认不是即时的。银行账户验证、mandate 授权、扣款提交和最终成功可能横跨数个工作日。

接入 ACSS 时，商户最需要提前设计三个环节：确认客户银行账户支持的币种、在扣款前取得符合规则的 mandate，以及在支付最终确认前控制履约。退款同样需要小心，因为 Stripe 退款会作为单独的入账发送给客户，并不撤销原始扣款；客户也可能同时向银行提出争议，造成双重返还。

## ACSS/PAD 的适用范围

Stripe 当前文档说明，加拿大和美国的 Stripe 商户可以向持有加拿大银行账户的客户收取 PAD。客户账户所在地应为加拿大，支付展示币种可为 CAD 或 USD。账户可能需要审核，使用时还要在 Dashboard 启用相关能力。

最常见的币种问题是银行账户和扣款币种不匹配。大多数加拿大银行账户以 CAD 持有资金，部分账户持有 USD。CAD 账户未必能够成功接受 USD 扣款，USD 账户也未必能接受 CAD 扣款。币种不匹配的失败通常不是立即返回，而可能要等最多 5 个工作日才确认。

建议默认使用 CAD，只有在确认客户银行账户支持 USD 扣款时才使用 USD。对于订单系统，应分别保存展示币种、扣款币种和 Stripe 结算币种，不要用商户结算币种代替客户银行账户币种。

## 先验证银行账户，再取得 PAD mandate

扣取银行账户前，商户必须收集 mandate，也称 pre-authorized debit agreement。该授权定义可扣款的时间表和条款，以及扣款是个人用途还是商业用途。每份 mandate 需要包括符合业务场景的付款计划和交易类型。

Stripe 可提供托管银行账户收集和 mandate 展示，也可以通过 Financial Connections 自动验证客户银行账户，替代手动输入 institution number、transit number 和 account number。若自动验证不可用，某些情况下需要通过微额存款验证。账户验证有助于减少无效账户导致的付款失败，但不能保证后续扣款一定成功。

对于自定义 PAD 授权页面，需遵循 Payments Canada Rule H1 和 Stripe 当前要求。商户应说明扣款授权、付款安排和客户权利，并确保授权内容在客户同意前可见。Stripe 文档还要求新 mandate 建立后在规定期限内向客户发送确认信息，且每次扣款需要提供相应通知。默认情况下 Stripe 会发送这些邮件；如果商户改为自发通知，需满足其审批和通知要求，不能只接管其中一部分邮件。

如果用于发票或订阅，要确认创建 mandate 时授权用途覆盖 invoice 或 subscription。关联客户与 PaymentMethod 后，仍应监控 mandate 是否取消或更新。客户可以随时通过商户或银行要求取消 mandate；取消后应停止未来扣款，若还需收款则重新收集授权。

## 最终付款需要异步确认

PAD 付款发起后，客户看到的通常是 submitted 或 processing 状态，而不是最终成功。Stripe 当前说明，最终确认可能需要最多 5 个工作日。扣款在提交日后进入银行处理；如果创建时间落在非工作日或超过银行处理截止时间，实际提交可能顺延。Charge 对象中的 expected_debit_date 是估计值，不是银行保证日期。

系统应区分客户完成支付表单、银行处理扣款和 Stripe 确认成功：

| 内部状态 | 含义 | 建议动作 |
| --- | --- | --- |
| mandate 已接受 | 客户允许未来按协议扣款 | 保存授权标识和条款版本 |
| payment_intent.processing | 扣款已经提交，等待银行处理 | 标记待确认，暂缓不可逆履约 |
| payment_intent.succeeded | Stripe 已确认付款成功 | 更新订单并按业务策略履约 |
| payment_intent.payment_failed | 银行或验证流程导致失败 | 通知客户并允许更换付款方式 |
| checkout.session.completed | 客户完成 Checkout 表单，但结果未最终确认 | 继续等待异步结果 |
| checkout.session.async_payment_succeeded | Checkout 延迟付款成功 | 更新订单为已付款 |
| checkout.session.async_payment_failed | Checkout 延迟付款失败 | 更新失败状态并通知客户 |

如果付款成功后银行稍晚通知 Stripe 失败，Stripe 可能通过争议对象反映该失败，原因可能与余额不足、账户资料不正确或银行无法处理有关。因此不要把“成功”当成永远不会变化的最终结论；应保留后续事件更新订单和余额记录的能力。

## 退款流程和双重入账风险

Stripe 当前说明，PAD 付款可以全额或部分退款，必须在原始付款后 180 天内提交，处理通常需要 3 个工作日。退款无法取消。如果原扣款仍在 pending 状态，退款会等 Charge 成功后才开始；如果 Charge 失败，Stripe 会取消待处理退款，因为客户实际上没有被扣款。

退款不是撤销原交易，而是 Stripe 对客户银行账户发起另一笔独立 credit。客户银行账单上这笔入账可能引用原始付款的 statement descriptor，而不一定明确标注“退款”。因此商户应在发起退款后主动告知客户预期到账时间，并提供订单金额、日期和账单名称供客户识别。

客户还可以向其银行提出 PAD 争议。Stripe 文档指出，个人账户通常有最多 90 个日历日提出争议，商业账户通常有最多 10 个工作日；争议只能提出一次，没有先行 inquiry 阶段。若商户退款与银行争议同时处理，客户可能收到两笔返还。

降低重复退款风险的具体做法：

1. 收到退款请求后，先检查是否已经收到 charge.dispute.created。
2. 联系客户确认商户准备发起 Stripe 退款，避免客户同时让银行处理同一笔交易。
3. 只有确认原始支付成功并完成结算后，再提交退款。
4. 退款创建后监控 Refund 对象，等待 refund.updated 或 refund.failed 事件。
5. 如果客户称银行已经处理返款，先暂停另一笔退款并由财务核对。
6. 只有在退款成功或替代处理完成后，才关闭订单的售后任务。

## ACSS 争议不能提交证据反驳

客户可以通过银行提出 ACSS/PAD 争议，Stripe 会发送 charge.dispute.created 事件，并从余额中扣除争议金额及适用费用。商户不能向 Stripe 提交证据或反驳 PAD 争议，银行决定最终且不可上诉，Stripe 不退还争议费用。

如果商户与客户协商同意客户重新付款，客户需要重新创建一笔付款。此操作要保留新旧支付对象的关系，避免把补付款当成原争议自动撤销。应及时向客户解释争议状态、可能的处理方式和新的支付凭证。

争议监控中应保存：

- Charge、PaymentIntent、Dispute 和内部订单 ID；
- 争议 reason 和事件时间；
- 原始付款币种及金额；
- 争议费用和 Stripe 余额变化；
- 客户沟通、退款记录及补付款关联；
- 订单履约和交付记录。

## Connect、Checkout 和产品能力限制

ACSS 可用于 Checkout、Payment Element、Invoicing、Subscriptions 和 Connect 的部分流程，但各产品仍有具体限制。Stripe 当前文档说明，Checkout 支持 payment 和 setup 模式，但 Checkout subscription mode 尚不支持 PAD；Express Checkout Element 和移动端 Payment Sheet 不支持。Payment Element 需要已有 PaymentIntent，Deferred Intent 或特定 Checkout Sessions API 流程也可能不支持。

Connect 平台要启用 PAD capability，并按 charge type 和 merchant of record 关系收集 mandate。使用 destination charge 和 on_behalf_of 时，需要为相应连接账户收集新的授权；不要假设平台客户的 PaymentMethod 和 mandate 可直接复制给连接账户使用。

配置前先确认账户、客户国家、支付产品、Connect charge type 和订阅流程都在支持范围。功能支持表可能变化，按账户 Dashboard 和 Stripe 文档现状为准。

## Webhook 与对账流程

至少监听支付成功、失败、争议创建与关闭、退款状态和 mandate 变化。Webhook 接收器要先验签，并通过 Event ID 或对象 ID 去重。处理事件时记录接收时间、Stripe 对象当前状态、内部任务状态和处理结果；失败后应能安全重试。

每日对账时分别检查：

- 发起支付金额和支付对象当前状态；
- expected_debit_date 与实际事件时间；
- Stripe 可用余额中的付款、退款、争议和费用；
- 退款成功金额是否已计入订单；
- 是否有一笔支付同时出现退款和争议；
- mandate 是否有效，订阅是否仍可扣款；
- 失败后客户是否已通过替代方式重新付款。

ACSS 的失败和争议可能在发起后多日才到达，因此日终报表不能只筛选当天新创建的支付。应定期重查 processing、近期成功以及近期退款的交易状态，确保后到事件不会被漏掉。

## 上线检查清单

- [ ] Dashboard 已启用 Canadian pre-authorized debit。
- [ ] 客户确实使用加拿大银行账户。
- [ ] CAD/USD 扣款币种与客户银行账户一致。
- [ ] Mandate 内容含有正确扣款安排、个人或商业用途和客户同意。
- [ ] 银行账户验证流程已测试，微额存款情形有处理说明。
- [ ] 付款 processing 不会被误标为成功。
- [ ] 订单依据异步 Webhook 确认最终付款结果。
- [ ] 退款仅在原始付款成功后提交，并跟踪最终状态。
- [ ] 退款前检查争议，避免 Stripe 退款与银行争议造成双重返还。
- [ ] 争议事件自动创建客服和财务任务。
- [ ] mandate 取消后，未来扣款和订阅重试会停止。

## 总结

ACSS/PAD 能为加拿大客户提供银行账户扣款和定期付款，但需要 mandate、银行账户验证和异步确认。业务系统必须等待 Stripe 的最终付款事件，正确匹配 CAD 或 USD，并关注最多 5 个工作日的处理窗口。退款应在原付款成功后发起，持续跟踪 Refund 状态，并在退款前检查银行争议，避免双重入账。

更多细节以 Stripe 和 Payments Canada 当前官方说明为准：

- [Stripe Canadian pre-authorized debit](https://docs.stripe.com/payments/acss-debit)
- [Stripe Financial Connections ACSS](https://docs.stripe.com/financial-connections/acss-direct-debit-payments)
- [Stripe Refund API](https://docs.stripe.com/api/refunds)
- [Payments Canada Rule H1](https://www.payments.ca/sites/default/files/h1eng.pdf)
