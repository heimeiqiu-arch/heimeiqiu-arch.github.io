---
title: "Stripe PayNow 新加坡二维码收款：有效期、退款与商户账单核对"
date: 2026-11-15
slug: "stripe-paynow-singapore-qr-code-expiry-refund-payout-guide"
description: "Stripe PayNow 如何创建新加坡 SGD 二维码付款，处理一小时过期、重复扫码、T+1 余额可用、90 天退款和 Connect 商户展示。"
keywords:
  - Stripe PayNow
  - PayNow 二维码 Stripe
  - Stripe PayNow 退款
  - PayNow QR 过期
  - Stripe 新加坡收款
tags:
  - Stripe
  - 支付方式
  - 新加坡
---

PayNow 是新加坡常见的实时付款方式，客户使用参与银行或金融机构的 App 扫描二维码并授权。Stripe 会为订单生成 PayNow QR 码，客户可以在电脑上用手机扫码，也可以在手机上保存二维码图片再通过支付 App 完成操作。二维码不是永久链接：若客户一小时内没有授权，支付会过期，需要回到页面重新开始并生成新的 PaymentIntent 和二维码。

这类支付有独特的结算和退款安排：付款确认后，资金通常在下一天进入 Stripe 余额，但最终 payout 仍受账户的打款排程影响；退款则受 90 天提交窗口和异步状态管理约束。本文梳理 PayNow 的适用条件、二维码体验、支付状态、退款与 Connect 责任，帮助商家避免重复收款、旧二维码复用和对到账时间的错误承诺。

## PayNow 的适用范围

PayNow 面向新加坡客户，展示币种为 SGD，Stripe 文档当前列出的最低金额为 0.50 SGD、最高金额为 200,000 SGD。商户账户所在地也需要是新加坡，且业务类别要符合 Stripe 和 PayNow 的资格要求。行业限制、账户审核和产品支持可能变化，商家应以 Dashboard 中的支付方式状态和当前官方文档为准。

PayNow 是一次性付款方式，不支持 recurring、SetupIntent 保存未来付款、off-session 扣款或手动捕获。它不能直接用于自动续费订阅。Billing 和发票场景也有特定限制：Stripe 文档当前说明 PayNow 不支持自动扣款，相关 Invoice 和 Subscription 需要使用 send_invoice 收款方式；Checkout 不支持在 subscription 或 setup mode 中使用 PayNow。产品需要续费时，应让客户选择支持周期扣款的方式，或通过人工发送发票并让客户每期主动付款（如账户适用）。

如果平台使用 Stripe Connect，还要考虑支付方式能力和 merchant of record。平台需启用 PayNow，并按集成模式为接受该支付方式的 connected accounts 申请 paynow_payments 能力。商户类别代码要设置正确，因为 Stripe 和 PayNow 使用 MCC 判断受限行业。Charge 类型会决定客户在 PayNow 页面或应用中看到平台还是 connected account 的商户名称。

## 二维码生成和一小时有效期

客户在 Checkout 或 Payment Element 选择 PayNow 后，Stripe 展示一个用于付款的 QR 码。桌面购买时，客户用手机扫描；移动端购买时，可能需要保存二维码图片，再切换到银行或支付 App 上传并授权。客户必须在二维码生成后的一小时内批准交易，超时后二维码失效，使用过期二维码会返回相应支付失败错误。

当二维码过期时，不能简单刷新页面并复用旧 QR 图片。系统应提示客户重新开始付款流程，由服务端创建新的支付会话或 PaymentIntent，并将新对象与内部订单状态关联。旧的 PaymentIntent 应保留为过期或未完成记录，以便客服和财务区分新旧尝试。对重新付款流程添加幂等保护，避免客户快速点击多次生成多张有效付款码。

一笔 PayNow 付款成功后，同一个二维码不能再次用于收款。若客户重复尝试，银行或支付 App 的拒绝行为可能不同；客服可以让客户检查银行 App 通知，确认是否已经付款。平台应按订单和 Stripe 对象核对，不能只看扫描次数或客户截图判断重复扣款。

## 服务端确认与订单履约

PayNow 的支付流程需要后端驱动订单状态。创建 PaymentIntent 时保存内部订单编号、客户和金额等业务关联；客户端展示 QR 码并等待用户操作；服务端通过 Webhook 或 API 查询确认支付结果后，再执行发货、开通数字内容或创建订单完成通知。

Webhook 接收端必须验证签名，记录 Stripe Event ID，并对重复事件幂等处理。事件被重试时，不得重复创建出库单或重复开通用户权益。也不要让 return URL 成为唯一成功依据：客户可能完成支付后没有返回浏览器，或访问了旧的成功页。每次返回页面都应该查询该订单关联的最新 PaymentIntent 状态，再展示“待授权、已支付、已过期或失败”等信息。

## 付款结算与账单描述

Stripe 文档当前说明，PayNow 付款完成后，资金通常在交易后一日进入 Stripe 余额；进入 Stripe 余额并不等同于已经到达商户银行。实际 payout 日期还取决于账户排程。例如，自动每日打款和每周打款会产生不同的银行到账节奏。商家应该把“付款成功、余额可用、payout 创建、银行到账”作为不同阶段展示和对账。

PayNow 不支持自定义 statement descriptor。客户银行流水和支付 App 中会显示 Stripe 的商户描述、付款金额以及 Stripe 生成的参考号；在 Connect 场景下，显示的平台或连接商户名称取决于 charge type。不要在订单页承诺银行流水一定显示你自定义的商店名称。客服可通过 Charge 对象的 PayNow reference 与客户核对付款记录。

## 退款时间窗与失败恢复

PayNow 支持全额和部分退款。Stripe 文档当前说明退款必须在原付款后 90 天内提交，退款处理异步进行，可能需要最多五分钟，并且提交后不能取消。90 天是支付方式允许的提交窗口，不代表商户的退款政策必须持续这么久；商家仍应明确自己的退换货规则和退款审批流程。

发起退款后，Refund 状态会先处于 pending，之后变成 succeeded 或 failed。监听 refund.updated 和 refund.failed，验证 Webhook 签名，并以 Refund 对象的最终状态为准更新订单和财务账本。若退款失败，Stripe 会把金额返回到余额，商家需要通过其他方式把款项退给客户。不能因为 API 创建 Refund 成功就向客户保证退款已完成。

建议退款通知告诉客户退款金额、提交时间和预计处理窗口，并给出内部支持联系路径。把退款 ID、原付款 ID、客户订单号、最终状态、失败原因和备用退款安排保存在同一组审计记录中。重复收到退款事件时，通过 Refund ID 和 Event ID 去重，避免重复退还。

## 常见问题排查

**客户扫描后没有付款。** 检查 PaymentIntent 是否仍在等待授权、二维码是否超过一小时、客户是否在银行 App 最终确认。过期后提示创建新支付，而非复用旧二维码。

**客户说支付成功但订单没更新。** 通过 PaymentIntent ID 查询 Stripe 最新状态，检查 Webhook endpoint 是否返回成功、签名校验和事件幂等是否正常。可安全地重新运行内部履约任务，但应先确认订单没有重复处理。

**客户重复扫描或付款。** 核对 Stripe 上是否存在一笔或多笔成功 PaymentIntent，联系客户确认银行 App 通知，并按退款政策处理多收款。相同 QR 码在成功后应被拒绝再次使用。

**退款迟迟未完成。** 查询 Refund 状态与事件。PayNow 退款可能异步处理，需等最终状态；若失败，则安排其他退款方式并保存 Stripe 余额返还的对账记录。

**银行账单不显示商店名称。** PayNow 不支持自定义 statement descriptor。向客户说明 Stripe 描述与系统生成的交易参考，并使用订单日期、金额和 reference 匹配。

## 上线验证清单

在测试环境验证 QR 展示、扫码授权、客户返回、二维码过期、旧码重用、重复创建 Session、Webhook 重试、部分退款、退款失败和 Connect 账户商户名称。检查 SGD 金额边界、Stripe 余额可用时间、自动与每周 payout 排程，以及 send_invoice 的适用业务流程。确保客服能用 Stripe reference 或 PaymentIntent ID 查到对应订单。

PayNow 的成功接入依赖正确管理短期二维码、服务端付款确认和异步退款。将 QR 生命周期、订单履约和 payout 时间分开记录，并明确银行账单描述和支付方式限制，才能让新加坡客户顺利完成付款，也让商家准确解释钱何时到账。

## 官方资料

- [Stripe：PayNow 支付](https://docs.stripe.com/payments/paynow)
- [Stripe：PayNow 收款接入](https://docs.stripe.com/payments/paynow/accept-a-payment)
- [Stripe API：创建退款](https://docs.stripe.com/api/refunds/create)
- [Stripe API：退款对象](https://docs.stripe.com/api/refunds/object)
- [Stripe：Connect 费用类型](https://docs.stripe.com/connect/charges)
