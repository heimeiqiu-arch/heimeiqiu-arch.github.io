---
title: "Stripe UPI 印度收款与 AutoPay：e-mandate、预扣通知和争议期限"
date: 2026-11-15
slug: "stripe-upi-india-autopay-emandate-recurring-refund-dispute-guide"
description: "Stripe UPI 如何处理印度 INR 即时支付、QR 和 App 跳转、UPI AutoPay mandate、至少提前 24 小时通知、退款以及七天争议证据期限。"
keywords:
  - Stripe UPI 支付
  - Stripe UPI AutoPay
  - UPI e-mandate Stripe
  - UPI 退款 7 个工作日
  - Stripe UPI dispute
tags:
  - UPI
  - 印度收款
---

UPI 是印度的实时支付系统，客户使用银行或钱包 App 授权付款。桌面用户可以扫描二维码，移动用户会跳转到 UPI App。Stripe UPI 除一次性付款外，还支持通过 e-mandate（也称 UPI AutoPay）设置后续自动付款。循环扣款必须符合客户在 UPI App 中批准的 mandate 条款；在后续扣款前，Stripe 或其支付合作方还要发送预扣通知，并至少等待 24 小时才尝试扣款。

一次性支付、首次建立 mandate、后续 off-session 扣款的状态与授权要求不同。UPI 也有严格的退款窗口和争议证据期限：退款最长可在原交易 60 天内提交，争议证据期限为 7 个日历日，而且只允许一次完整提交。本文整理商户资格、扫码支付、AutoPay 生命周期、退款、争议和对账要点。可用国家、行业和支付规则会更新，请上线前查看 Stripe Dashboard 和当前文档。

## 客户、币种和金额资格

UPI 面向印度客户，交易币种为 INR，Stripe 文档当前列出的单笔金额范围为 1 至 100,000 INR。UPI AutoPay 的每次自动扣款上限为 15,000 INR。商户账户所在国家可以是 Stripe 文档列出的多个国家，但客户位置和币种仍受限；不应把“Stripe 商户账户在支持国家”误解为可以向任意国家消费者使用 UPI。

账户资格还受行业限制和 Stripe 审核影响。某些 MCC 被禁止或需要额外材料，完整清单很长，需根据企业业务类型核对官方列表。启动集成前确认 Payment Method Settings 中 UPI 已启用，并测试实际 Dashboard 和 API 配置，而不是根据同地区其他商户的经验推断。

## 一次性支付：App 跳转和二维码

客户在结账页面选择 UPI 后，可通过移动银行或钱包 App 完成授权；桌面流程可以显示 QR 码供 UPI App 扫描。Stripe 对已在客户现场完成的一次性 UPI 支付通常即时确认，但客户可能在授权页面中途退出或未批准。应用需根据 PaymentIntent 的最终状态决定订单是否付款，不要只根据二维码生成、页面跳转或客户端回调发货。

在服务器端创建 PaymentIntent 或 Checkout Session 时，保存内部订单 ID、金额、币种和 Customer 关联。Webhook 接收端验证签名，记录 Event ID，并幂等更新订单。对于客户已经批准但浏览器未返回的情况，以 Stripe 对象和事件为准；对同一事件重试，不能重复创建出库单或发放数字权益。

## UPI AutoPay：收集并管理 mandate

首次设置循环付款时，客户需要在 UPI App 中审核并批准 e-mandate。授权中可包含固定金额或最高金额、结束日期等条件。UPI PIN 等认证由客户在其 UPI App 完成，商户不应采集或记录银行 PIN。授权说明应清楚，让客户知道未来扣款用途和边界；金额和频率要落在 mandate 批准范围内。

Stripe Mandate 对象包含 UPI 专属授权详情，例如 description、amount_type、amount 和 end_date。较早创建的 mandate 可能没有所有字段；Dashboard 也不一定显示 mandate 全部细节，因此业务系统要按需要通过 API 查询并保存授权快照。保存 PaymentMethod 与 Mandate ID，并记录授权状态变化和对应订阅。

后续 UPI AutoPay 付款是异步确认。扣款前 Stripe 或合作方会发出预扣通知，等待至少 24 小时后再尝试。不能在创建续费发票时立即假设款项已收，也不要在通知未完成时自行发起相同金额的额外扣款。用 invoice、PaymentIntent、Mandate 和 Subscription 关联每一周期，分别处理预扣通知、扣款尝试、成功和失败事件。

UPI mandate 撤销与 PaymentMethod 解绑是两个独立动作。客户可在 UPI App 中随时取消 mandate；Stripe 收到撤销后会通过 mandate.updated 通知，Mandate 状态变为 inactive。Stripe 无法替客户取消其 UPI mandate。若客户要求停止未来收费，企业应立即停止发起新扣款，并同步订阅状态；仅 detach PaymentMethod 不等于撤销 mandate，反过来也不能因为 Dashboard 仍显示 PaymentMethod 就继续扣款。

## 退款处理：60 天窗口和七个工作日

UPI 支持全额和部分退款，Stripe 文档当前要求在原付款后 60 天内提交。退款异步处理，可能最多需要 7 个工作日，且提交后不可取消。退款申请的 API 响应不能作为资金已退回的证明，客服应说明实际处理仍以 Refund 对象的最终状态为准。

监听 refund.updated 和 refund.failed，或在 Dashboard/API 查询 Refund 对象。状态变为 succeeded 后更新账务为已退款；若变成 failed，Stripe 会将退款金额返回 Stripe 余额，商户需要通过其他方式退给客户。保存退款 ID、原 PaymentIntent、订单号、金额、客户通知和失败处理人，避免通过另一个渠道重复退还。

## 争议与证据一次性提交

UPI 客户可以通过银行对付款发起争议。Stripe 会暂扣相关争议金额并通过 Dashboard、邮件和 charge.dispute.created 通知。客户最多可在购买后 90 个日历日内发起争议；商户通常只有争议创建后 7 个日历日提交证据。具体期限应使用 Dashboard 或 Dispute.evidence_details.due_by，而不是按经验估算。

UPI 争议只允许一次证据提交，之后不能补充。因此收到通知后，先收集时间戳服务日志、物流和签收证明、页面条款、客户邮件、用户操作记录、退款凭证与商品访问记录，统一检查后一次性提交。为每个 Dispute ID 设置内部截止提醒和责任人。证据不应只包含泛化说明，要能够证明客户授权、商品或服务交付、退款政策展示和售后沟通。

胜诉时争议金额会返还 Stripe 余额；败诉时扣款可能成为永久损失。不要将争议状态与退款状态混为一谈，也不要在争议尚未结案时同时无条件再次退款。财务应关联 Dispute、PaymentIntent、Charge、Balance Transaction 和订单。

## 对账和常见问题

**桌面 QR 支付没有确认。** 查询 PaymentIntent 状态和事件投递，确认客户是否在 UPI App 完成批准。二维码显示出来不等于已付款。

**AutoPay 续费未即时成功。** 后续扣款是异步的，还需预扣通知并等待至少 24 小时。检查 mandate 状态、金额上限和结算事件，不要立即重复扣款。

**客户已解绑 PaymentMethod，但 mandate 仍有效。** PaymentMethod detach 与 mandate 撤销相互独立。停止未来扣款，并依据 Stripe Webhook、Mandate 状态和客户在 UPI App 中的操作核实。

**部分退款累计超额。** 以原付款金额为上限，在内部退款账本对多笔 Refund 求和后再提交新退款。

**争议证据来不及准备。** 按 due_by 创建提醒；由于只能提交一次，先汇总全部相关材料再提交，保留证据文件和提交时间。

## 上线前核对清单

测试一次性 QR 与 App 授权、客户取消、一次性支付成功、AutoPay mandate 批准、首笔和后续扣款、预扣通知、15,000 INR 限额、客户撤销 mandate、PaymentMethod detach、全额与部分退款、退款失败以及一次性争议证据提交。检查金额、币种、账户资格、行业类别和 Webhook 幂等。财务和客服应能够按 mandate、付款、退款与争议 ID 查询同一客户账单周期。

UPI 的优势是本地实时支付并可在获得授权后支持自动扣款，但后续收费必须遵守 mandate 和通知时限。用服务端事件同步付款，通过 API 管理授权状态，并为 60 天退款和 7 天争议证据期限设置后台流程，才能让 UPI AutoPay 在订阅业务中稳定运行。

## 官方资料

- [Stripe：UPI 支付](https://docs.stripe.com/payments/upi)
- [Stripe：UPI AutoPay](https://docs.stripe.com/payments/upi/upi-autopay)
- [Stripe API：Mandate 对象](https://docs.stripe.com/api/mandates/object)
- [Stripe API：Refund 对象](https://docs.stripe.com/api/refunds/object)
- [Stripe API：Dispute 对象](https://docs.stripe.com/api/disputes/object)
