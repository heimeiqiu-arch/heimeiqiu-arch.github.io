---
title: "Stripe BLIK 支付接入：波兰验证码、循环扣款授权与争议响应"
date: 2026-11-15
slug: "stripe-blik-poland-payment-recurring-mandate-refund-dispute-guide"
description: "Stripe BLIK 如何收取波兰客户付款，管理 6 位数代码和银行 App 授权、保存循环扣款 mandate、跟踪异步退款并在期限内提交争议证据。"
keywords:
  - Stripe BLIK 支付
  - BLIK recurring payments Stripe
  - BLIK mandate
  - Stripe BLIK 退款
  - BLIK dispute evidence
tags:
  - 支付方式
  - 波兰
---

BLIK 是波兰常用的银行支付方式之一。客户从银行 App 取得 6 位数字代码，在结账页输入后，再到银行 App 中批准付款。这个流程和 P24 的跳转式银行选择不同：BLIK 页面通常不会把用户自动跳回商家，移动端客户可能需要手动切回网站查看结果。BLIK 还支持在首次设置时保存可复用的付款授权，用于以后符合条件的 off-session 循环扣款，因此它既能用于单次付款，也可能适用于订阅，但后者需要更严格地管理 mandate 和账户能力。

本文介绍 Stripe BLIK 的客户流程、资格和金额边界、首次循环付款授权、后续扣款、退款、争议证据以及 Connect 平台注意事项。Stripe 对支付方式能力、金额限制、账户国家和行业适用范围可能更新；上线前应核对当前 Dashboard 与官方文档，并以 API 返回结果为准。

## 客户付款流程与状态处理

客户在结账时选择 BLIK，从银行 App 生成 6 位数字代码并输入支付表单。代码有效期为 2 分钟；付款启动后，客户通常要在 60 秒内通过银行 App 批准。Stripe 一般会在 60 秒内收到 BLIK 的付款结果并更新页面。某些移动支付流程不会自动把客户重定向回商家页面，因此不能假设“用户回到 success URL”才代表交易成功。

结账页面应说明客户需要打开银行 App 批准通知，并保持当前支付页面等待结果。用户离开页面后，服务端仍需通过 Stripe Webhook 或查询 PaymentIntent 确认付款状态。将订单创建、收款确认和履约拆成不同状态，避免客户提交代码后就立即发货。若付款失败或用户未批准，订单应保持可恢复状态，并向客户提供重新付款的路径。

Stripe Checkout 是常见的集成方式；Payment Intents 与 Payment Element 也可用于受支持的流程。对移动端和网页端分别测试输入代码、切换到银行 App、批准、拒绝、超时、返回商家页面的体验。客户端只展示状态，后端通过签名验证、事件幂等和订单 ID 关联来触发履约。

## 资格、币种和金额限制

BLIK 面向波兰客户，Stripe 文档列出的展示币种为 PLN，最低付款金额为 2.00 PLN。文档当前还列出一次性支付的单笔上限，以及 off-session 循环扣款的单笔上限；这些限制与一次性和后续扣款场景不同，系统应按交易类型进行校验，而不是共用一个金额判断。

商户账户所在国家也会影响支付方式资格。Stripe 对 BLIK 支持多个商户账户地区，但客户需要位于波兰，且商户账户必须具备对应能力。展示方式前，应检查 Payment Method Settings、账户状态、币种和客户位置。账户在支持地区并不保证特定商家类别无需额外审核。

BLIK 支持 recurring payment，但需要正确收集并管理客户授权。不能把客户首次输入的 BLIK 代码当成以后扣款的授权本身；必须采用 Stripe 支持的保存付款方式或 SetupIntent 流程，让客户在银行 App 中授权未来扣款条件。向客户说明未来付款的目的、频率或可变金额逻辑，并保存可追溯的授权记录。

## 设置可复用付款方式和 mandate

若客户在首次付款时授权未来扣款，可使用 PaymentIntent 的 setup_future_usage=off_session；若尚不收取首笔款项，可使用 SetupIntent 并设 usage=off_session。Stripe 会把授权与可复用的 BLIK PaymentMethod 和 mandate 关联。实现前确认当前产品、API 和账户资格支持该用法；不要在浏览器中自行存储 BLIK 验证码，也不要保存银行登录凭据。

后续 off-session 扣款应使用已授权的 PaymentMethod，并遵守授权范围。订阅价格、收费频率或用途发生实质变化时，重新评估是否需要更新或重新取得客户授权。Stripe Mandates API 可用于读取和管理 mandate；若 mandate 被客户撤销或过期，应先重新收集授权再尝试后续付款。

如果客户要求停止未来 BLIK 扣款，解除关联可复用 PaymentMethod 会撤销未来使用授权；客户也可在自己的银行 App 中撤销。取消订阅与撤销 PaymentMethod 是两个独立动作，应同时更新计费安排、本地权限和 mandate 状态。一个动作成功不能替代另一个动作的确认。

在 Stripe Connect 中，平台和接受 BLIK 的 connected account 都需要具备适用能力。Recurring BLIK 还涉及单独的 recurring capability，文档要求先后申请基础 BLIK 能力与 recurring 能力，并在平台及相关 connected account 上确认激活。平台不要仅检查自身能力后就向所有商户开放订阅扣款。

## Webhook 与订阅生命周期

Webhook 接收端需要验证签名、记录 Event ID 并保证幂等。根据实际集成监听 PaymentIntent、SetupIntent、Customer、Subscription 和 Mandate 相关事件。支付成功只更新对应订单或账单；SetupIntent 成功则要可靠保存 PaymentMethod ID 和内部客户关联。避免只在前端授权回调中写入付款方式，因为客户可能关闭网页或恶意修改浏览器请求。

对订阅场景，分别追踪首次授权、首笔付款、后续续费扣款、失败重试和取消 mandate。每个周期 invoice ID、PaymentIntent ID 和 PaymentMethod ID 都应有对应记录。付款失败时不要无限自动重试，也不要在用户已经撤销授权后继续提交扣款；应根据 Stripe 当前状态通知客户重新授权或选择另一付款方式。

## 退款处理与客户沟通

BLIK 支持全额和部分退款。Stripe 当前文档说明原付款后 730 天内可提交退款；这个时间是支付方式的最大处理窗口，不是商家对客户退款政策的承诺。BLIK 退款异步处理，银行端可能最多需要约 120 分钟。提交后通常不能取消，因此发起前核对付款、金额和客户身份。

退款会退到客户银行账户。提交退款成功后，读取 Refund 对象状态，并监听 refund.updated 或 refund.failed。status=succeeded 表示 Stripe 报告退款成功；如果变为 failed，Stripe 会把金额退回 Stripe 余额，商家需要与客户安排其他退款方式。系统应为失败退款创建客服或财务任务，而不是将原付款简单改为“已退款”后结束。

给客户的退款通知包含金额、币种、提交时间和预计处理时间；同时保存 Refund ID、原 PaymentIntent 或 Charge ID、事件 ID 和最终状态。通知成功不等于退款成功，银行处理时间也可能不同于客服邮件送达时间。对账时保持支付与退款两条记录，确保可追踪净额变化。

## 争议处理与证据期限

BLIK 仍可能发生争议。Stripe 文档说明，争议发生后会从余额中暂扣相关金额，并通过 Dashboard、邮件和 webhook 通知商家。争议证据提交期限以 Dispute 对象 evidence_details.due_by 或 Dashboard 展示为准。文档当前说明商家通常有 12 个日历日从争议创建时提交证据；个案始终应以实际对象期限为准。

可准备的证据包括订单履行或物流跟踪、数字商品访问和下载记录、客户购买凭证、服务交付证明、客户沟通以及退款记录。保存原始证据和提交时间，并由负责人员检查附件是否对应正确的争议和付款。若证据提交期限将至，先准备可用材料并提交，再补充内部复盘，不要因等待完整调查错过截止时间。

BLIK 的争议流程与信用卡拒付不同。Stripe 文档指出，BLIK 不收取争议费用且争议决定不可上诉。获胜时争议金额会返还余额；若裁决支持客户，扣款会成为永久损失。把争议状态和客户后续退款状态分别记录，避免同一争议重复退款或错误恢复服务。

## 常见问题排查

**客户输入 BLIK 代码后页面一直等待。** 检查客户是否在 60 秒授权窗口内批准、PaymentIntent 当前状态、Webhook 是否延迟以及前端是否正确轮询。不要仅因浏览器没有自动返回就重复创建付款。

**想把 BLIK 用于订阅。** 验证支持地区、Recurring 能力、off-session 上限和 mandate 是否已建立；没有客户有效授权时，不要尝试后台扣款。

**续费失败但客户仍显示已授权。** 检查 PaymentMethod 与 mandate 状态、Customer 关联、金额限制和实际付款结果。授权存在不代表每次扣款必然成功。

**客户说已经在银行 App 取消授权。** 读取 PaymentMethod 和 mandate 当前状态，停止后续 off-session 扣款，并处理订阅是否继续、是否更换付款方式。

**退款未到账或失败。** 查询 Refund ID 和 webhook；对异步处理等待 Stripe 最终状态。退款失败时，按另一种方式退还客户，并留存原退款失败记录。

## 上线验证清单

测试一次性付款成功、拒绝授权、代码超时、客户切换 App 后返回、重复 Webhook、SetupIntent 建立授权、首次订阅扣款、后续 off-session 付款、客户撤销 mandate、部分退款、退款失败和争议通知。检查 PLN 金额边界、Connect 平台及 connected account 能力、Dashboard 交易状态与内部订单账本是否一致。客服需要能够按订单、PaymentIntent、Refund 和 Dispute ID 查询。

BLIK 能把银行 App 授权融入本地结账，也能在符合条件并取得授权后用于后续循环扣款。把一次性付款、mandate 建立和后续扣款作为不同步骤管理，使用 Webhook 确认服务端状态，并单独追踪退款与争议，能显著降低重复扣款、错误发货和授权失效后的投诉风险。

## 官方资料

- [Stripe：BLIK 支付](https://docs.stripe.com/payments/blik)
- [Stripe：BLIK 循环付款](https://docs.stripe.com/payments/blik/recurring-payments)
- [Stripe：保存 BLIK 付款方式](https://docs.stripe.com/payments/blik/save-during-payment)
- [Stripe API：Mandates](https://docs.stripe.com/api/mandates)
- [Stripe API：退款对象](https://docs.stripe.com/api/refunds/object)
