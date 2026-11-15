---
title: "Stripe Boleto 巴西付款凭证管理：有效期、异步确认与订单履约"
date: 2026-11-15
description: "介绍 Stripe Boleto 的巴西账户资格、付款凭证有效期、Webhook 异步确认、订单匹配和不支持退款的运营边界。"
slug: "stripe-boleto-voucher-expiration-async-payment-fulfillment-guide"
tags: ["Stripe", "Boleto", "巴西支付", "异步付款"]
keywords: ["Stripe Boleto", "Boleto 付款凭证", "Boleto 支付状态", "Stripe Boleto Webhook", "巴西凭证付款"]
---

# Stripe Boleto 巴西付款凭证管理：有效期、异步确认与订单履约

Boleto 是巴西常见的凭证式付款方式。客户在 Stripe Checkout 或其他支持的页面生成付款凭证，再通过银行、ATM、授权代理点或网上银行完成付款。生成凭证并不代表订单已经付款；只有客户实际支付并且 Stripe 异步确认后，商户才能将订单更新为已付款。

这种两阶段流程会影响库存保留、优惠券、履约和客户支持。凭证有有效期，客户可能在生成后几天才付款；付款通知又通常要到下一个工作日才确认。本文说明如何设计凭证生命周期、使用 Webhook 更新订单、避免将凭证编号当成交易编号，以及在不支持 Stripe 退款的前提下如何处理售后政策。

## 先核对商户和订单资格

Stripe 当前文档说明，Boleto 面向巴西商户和巴西客户，交易使用巴西雷亚尔 BRL。当前文档列出的单笔金额范围为 BRL 5.00 至 BRL 49,999.99。上线时应以 Dashboard 和最新 Stripe 文档为准，并确认你的商户账户已启用 Boleto。

Boleto 需要客户提供所需的联系和税务识别资料。创建后，Stripe 会展示托管凭证页面，客户可以复制 Boleto 号码或下载 PDF。客户可在银行、ATM、授权代理点或网上银行支付。

接入前确认：

| 项目 | 核对内容 |
| --- | --- |
| 商户所在地 | Stripe 账户是否位于巴西并获准使用 Boleto |
| 客户所在地 | 客户是否在巴西，订单是否为国内付款场景 |
| 交易币种 | 订单和支付请求使用 BRL |
| 金额范围 | 是否符合当前 Dashboard 显示的支付限制 |
| 客户资料 | 结账流程能否收集所需联系和税务资料 |
| 产品支持 | 选择的 Stripe Checkout、Payment Links、Elements 或其他产品是否支持 Boleto |

Stripe 文档将 Checkout Sessions 列为推荐 API，也列出 Payment Links、Payment Element、Invoicing 和 Connect 等支持场景。不同产品具体限制可能不同，先从当前集成方式的官方指南核对，再决定是否手工指定支付方式。

## 凭证有效期和待付款订单状态

Boleto 凭证默认有效期为 3 天，Stripe 文档说明可以配置为 0 至 60 天。有效期会影响库存、报价和订单管理：有效期越长，客户越有时间付款，同时商户要更久地保留库存或价格承诺。

不要把未付款的凭证长时间保留为“待支付但已履约”。业务系统可以采用以下状态：

| 内部状态 | 触发条件 | 业务动作 |
| --- | --- | --- |
| 待付款 | 已生成凭证，客户尚未付款 | 显示付款指引，按政策保留库存 |
| 凭证即将过期 | 距离配置有效期较近 | 发送提醒，提示客户在有效期内完成付款 |
| 已过期或无法继续支付 | 凭证达到截止时间或支付对象已失败 | 释放库存并关闭待付款订单 |
| 付款处理中 | 客户已支付，Stripe 正等待异步确认 | 暂不重复生成凭证或判定失败 |
| 付款成功 | Stripe 确认付款成功 | 更新订单并启动履约 |
| 付款失败 | Stripe 报告失败 | 通知客户并允许按业务规则重新创建支付 |

如果库存有限，明确说明保留时长和付款有效期的关系。客户在凭证过期后付款或系统收到迟到通知时，订单可能已经取消或库存已分配给其他客户。需要制定人工处理流程，核对实际资金状态、库存可用性和客户选择，再决定是否履约或处理订单。

## 依靠服务器端事件确认付款

Boleto 付款确认异步进行，Stripe 当前说明通常在客户付款后的下一个工作日确认。不能只根据前端凭证页面跳转、浏览器返回或付款凭证生成事件触发发货。

对 Checkout，checkout.session.completed 可能表示客户完成了 Checkout Session，但对于 Boleto 这类延迟支付方式，商户仍应等待 checkout.session.async_payment_succeeded 或 checkout.session.async_payment_failed 来确认最终支付结果。对 PaymentIntents，则要根据 payment_intent.processing、payment_intent.succeeded 和 payment_intent.payment_failed 更新状态。

建议的处理逻辑：

1. 创建 Stripe Checkout Session 或 PaymentIntent 时，将内部订单 ID 与 Stripe 对象关联。
2. 凭证生成后记录会话 ID、PaymentIntent ID、凭证显示信息、金额、币种和到期时间。
3. 客户下载或复制凭证时，订单仍保持待付款。
4. 服务端收到并验签成功的异步成功事件后，更新付款状态并启动履约。
5. 收到失败、过期或取消状态后，释放库存或按政策关闭订单。
6. 重复 Webhook 到达时，通过 Event ID 和支付对象状态去重，不重复履约或发送通知。

前端可以展示“凭证已生成”和“等待付款确认”，但不能由客户端自行把订单标记为成功。Webhook 接收端应验证签名，并将事件 ID、对象 ID 和处理结果写入日志。若仓储、邮件或 CRM 暂时不可用，应保存事件并重试下游动作。

## Boleto 凭证号码不是交易 ID

Stripe 文档指出，可以从 PaymentIntent 的 next_action.boleto_display_details.number 获取客户看到的 Boleto 号码。该号码用来标识付款凭证，但不是处理器交易 ID；Boleto 的 latest_charge.payment_method_details.boleto 下不会提供一个 processor transaction ID。

客服和财务对账时，应同时保存：

- 内部订单编号；
- Checkout Session 或 PaymentIntent ID；
- Boleto 凭证号码；
- Charge ID（若已创建）；
- 金额、币种和创建时间；
- 凭证有效期；
- Webhook Event ID 和最终付款状态。

不能仅靠凭证号码来证明资金已到账，也不要将其作为所有 Stripe 数据系统间唯一关联键。若客户提供银行回单，客服可以用金额、日期、凭证号码和内部订单共同查找，但最终付款确认仍应依据 Stripe 支付对象和事件状态。

Boleto 凭证或银行回单可能显示 Stripe 作为公司名称，具体格式取决于客户银行和付款渠道。商户可以按非卡支付方式配置 statement_descriptor，但银行可能以不同格式展示，或省略部分描述。不要承诺客户的银行账单一定逐字显示商户名称。

## 订单与库存的实务规则

生成凭证后可以选择短时预留库存，也可以在付款确认后才锁定库存。两种设计应与商品特性匹配：

- 实物库存紧张时，配置明确的保留期限，并在凭证过期后释放库存。
- 数字商品或服务可能存在重复交付风险，应在付款成功 Webhook 中按订单 ID 幂等触发。
- 促销价格有限时，说明价格是否保留至凭证到期，避免客户按过期凭证付款后发生纠纷。
- 高金额 B2B 订单可先核对买方资料和税务信息，再生成付款凭证。
- 如果付款成功事件到达时订单已取消，进入人工队列检查库存和资金，避免自动重复建单或无货发货。

可以将“订单接受 Boleto”“凭证生成”“客户付款”“Stripe 确认”“订单履约”视为独立事件。这样客服可以准确回答客户：订单目前只是等凭证付款，还是银行已扣款但 Stripe 尚未确认。

## Stripe 不支持 Boleto 退款时的售后处理

Stripe 当前 Boleto 支付方式说明列出不支持全额或部分退款。因此，设计售后和退货政策时不能默认所有其他支付方式的 Stripe Refund API 工作流都适用于 Boleto。客户要求退款时，先确认账户可用的支持方式和业务政策，并按 Stripe 当前文档和当地规则决定如何处理。

处理时应特别注意：

- 核对 Stripe 支付是否已经成功，避免对未实际扣款的凭证处理退款。
- 保存客户退款申请、订单、金额、收款凭证和内部批准记录。
- 向客户说明预计处理方式和时间，不要用“Stripe Refund 已创建”描述未支持的流程。
- 如果使用其他退款渠道，记录独立的付款凭证、币种、时间和经办人。
- 将替代退款关联到原 Stripe PaymentIntent 和内部订单，避免财务把原付款与替代付款分开遗漏。
- 如果发生银行侧异常或客户反馈付款处理不正确，按 Stripe 通知联系支持并跟踪案件。

Stripe 文档说明 Boleto 不使用标准银行卡争议流程，客户不能发起卡组织 chargeback；但某些银行侧异常仍可能发生，Stripe 会联系商户说明下一步。不能把“无标准拒付”误解为没有客户投诉或银行问题。客服仍需保留凭证、付款结果和客户沟通记录。

## 异常场景排查

### 客户称已付款，但订单仍是待付款

先检查 PaymentIntent 或 Checkout Session 的状态、Webhook 接收日志和事件是否重试。银行渠道的支付状态可能在下一个工作日才更新。不要让客户重复付款，先通过凭证号码、订单信息和付款时间核对交易。

### 凭证已过期，客户仍要求付款

检查 Stripe 对象当前状态和事件历史，确认是否还能通过原凭证付款。若已失效，按当前官方流程创建新支付对象和新凭证，并将旧凭证标记为关闭或过期。不要在系统中重新打开旧订单而不核对库存与金额。

### 同一凭证被多次提交或生成多个会话

创建支付对象时对内部订单使用幂等控制，避免用户连续点击按钮生成多张有效凭证。若确实生成了多个会话，明确哪一个是有效订单付款入口，并将其他会话状态同步到客服与库存系统。

### 银行回单与 Stripe 状态不一致

记录客户回单并核实金额、币种、付款时间和 Boleto 号码，再查 Stripe 对象和异步事件。回单可作为排查材料，但不应绕过 Stripe 状态直接触发高风险履约。

## 上线前检查清单

- [ ] Dashboard 确认账户有 Boleto 能力。
- [ ] 商户、客户、币种和金额符合巴西支付场景。
- [ ] 凭证有效期与库存保留和报价政策一致。
- [ ] 凭证生成后订单不会被标记为已付款。
- [ ] Checkout/PaymentIntent 的异步事件映射到正确订单。
- [ ] Webhook 验签和事件去重已实现。
- [ ] 订单保存凭证号码及 Stripe 对象 ID。
- [ ] 退款政策考虑到 Stripe 当前不支持 Boleto Refund。
- [ ] 银行侧异常和付款晚到有人工处理路径。
- [ ] 付款成功、失败、过期和迟到事件都在测试中覆盖。

## 总结

Boleto 的核心运营特征是凭证先生成、客户之后付款、Stripe 再异步确认。配置 0 至 60 天的有效期时，需要同步考虑库存和价格；履约应等待服务器端确认事件；凭证号码只是客户付款凭证标识，不是 Stripe 交易 ID。退款政策也应针对 Stripe 当前不支持 Boleto Refund 的限制设计，并保留银行侧异常的客服处理流程。

- [Stripe Boleto 支付文档](https://docs.stripe.com/payments/boleto)
- [Stripe Checkout 延迟付款](https://docs.stripe.com/payments/checkout)
- [Stripe PaymentIntent API](https://docs.stripe.com/api/payment_intents)
- [Stripe Webhook 签名验证](https://docs.stripe.com/webhooks/signature)
