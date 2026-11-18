---
title: "Stripe Zip 分期支付：澳美资格、退款去向和争议流程差异"
date: 2026-11-15
slug: "stripe-zip-australia-us-buy-now-pay-later-refunds-disputes-guide"
description: "Stripe Zip 如何按澳大利亚或美国客户筛选分期方案，理解商户先收款、退款返还差异、美国与澳大利亚争议处理区别。"
keywords:
  - Stripe Zip 分期付款
  - Zip Stripe 退款
  - Stripe Zip 澳洲美国
  - Zip dispute Stripe
  - Stripe Buy Now Pay Later
tags:
  - Zip
  - 分期付款
---

Zip 是面向澳大利亚和美国消费者的先买后付支付方式。客户在结账时离开 Stripe 页面，登录或创建 Zip 账户，选择可用的还款方案并批准。Stripe 会将购买金额（扣除费用）提供给商户，Zip 再按照消费者的计划直接收取还款。商户收到的是订单付款，不是每期从 Zip 收到消费者的分期款。

Zip 在美国和澳大利亚的方案、退款去向和争议处理完全不同。美国 Zip 付款争议由 Zip 直接管理；澳大利亚争议则会经 Stripe Dashboard 和 Webhook 通知，商户需要在 12 天内提交证据。退款方面，美国未付分期会取消并退回已付款到原资金来源；澳大利亚的退款会记入客户 Zip 余额。本文梳理资格筛选、方案门槛、订单确认与国家差异，具体资格和额度以当前 Stripe Dashboard 和 Zip 授权页面为准。

## 商户国家、消费者国家和交易币种

Stripe 文档当前将 Zip 支持范围列为澳大利亚和美国商户与消费者，交易为国内本地付款，不支持跨境交易。澳大利亚客户需要澳大利亚商户账户和 AUD 交易，美国客户需要美国商户账户和 USD 交易。若 Checkout 动态支付方式已启用，Stripe 会根据配送地址国家（若有）或客户端 IP 国家判断是否展示 Zip。

如自行列出 payment_method_types，商户需自行保证仅向支持国家的消费者展示 Zip；不能把 Zip 按钮面向所有访客。业务类别也受到澳大利亚和美国分别适用的 MCC 规则限制，某些行业禁止，另一些需要补充材料。启用前先查看 Stripe 的完整类别清单和账户设置。

## Zip 方案由国家、金额和客户资格决定

澳大利亚客户可能看到 Zip Pay 或 Zip Money。Zip Pay 适用于较低金额，并允许客户选择每周、每两周或每月还款；账户费用、月费和免除条件由 Zip 的产品条款决定。Zip Money 对应较高的金额范围，可能提供更长免息期，但需批准，商户也需满足相关资格。

美国 Zip Pay in 4 的购买金额范围和还款节奏与澳大利亚不同。Zip 对客户费用和资格有自己的审批规则，商家不能保证每个客户都能看到相同的计划、期限或费用。最终方案应以 Zip 授权页面显示的条款为准，不要把示例月供或零利息方案写成无条件承诺。

商户可以使用 Payment Method Messaging Element 在结账前展示分期信息，但必须遵守 Zip 针对美国和澳大利亚的品牌与营销规范。优惠、税款、运费和商品金额应先由服务端确定，再把准确订单总额提交给 Stripe。

## 结账跳转和商户到账

客户在 Stripe Checkout 选择 Zip 后，会进入 Stripe 托管跳转，再继续到 Zip 托管页面完成资格检查和方案选择。客户授权后返回商家 return URL，Stripe 会报告支付成功或失败。服务端仍应确认 PaymentIntent 或 Checkout Session 状态，并通过验签 Webhook 更新订单，不要只根据浏览器到达成功页面履约。

支付成功后，商户通常提前收到完整购买金额扣除费用；消费者后续向 Zip 还款不再是商户的 Stripe 订单款项。订单和财务账本记录 PaymentIntent、Charge、Balance Transaction 与 payout，消费者分期计划由 Zip 管理。Zip 负责生成消费者账单描述，Stripe 的通用 statement descriptor 设置不会覆盖 Zip 的分期描述。

## 退款去向因国家而异

Stripe 当前文档允许原付款后 180 天内为 Zip 付款发起全额或部分退款。Refund 会先进入 pending，异步处理，通常在 Zip 处理退款确认后的 3 至 5 个工作日完成，但不保证固定时间；pending 的退款不能取消。

美国 Zip 退款时，Zip 会取消尚未支付的分期，并将客户已支付金额退回其原始付款方式。澳大利亚 Zip 退款时，全额或部分退款通常会记入客户可用的 Zip 余额。这一差异应在客服说明、退货政策和财务记录中体现：商家退回订单，不代表客户必然看到银行或银行卡上的同一种退款表现。

读取 Refund 对象状态并监听 refund.updated 或 refund.failed。退款成功后记录最终 Refund ID 和金额；失败时，Stripe 会将款项退回余额，商家需要通过其他方式向客户退款。不要仅凭退款请求创建成功就把售后工单关闭。

## 美国和澳大利亚争议流程不同

美国 Zip 争议由 Zip 自行管理通知、回应和结果。客户应联系 Zip Support，商家需要遵循 Stripe 或 Zip 针对该交易给出的流程，不应假设澳大利亚的 Stripe Disputes 提交入口同样适用。

澳大利亚客户通常需要先联系商家处理问题；如果购买后 14 天仍未解决，客户可能向 Zip 开案。成为正式争议后，Stripe 会暂扣争议金额和适用费用，并通过邮件、Dashboard 及 charge.dispute.created Webhook 通知。商户通常有 12 个日历日提交证据，具体以 Dashboard 和 Dispute 对象的截止日期为准。

证据可包括退货确认、物流单号、发货日期、数字产品访问或邮件收据、服务履行记录与客户沟通。保存争议对象、原订单和 Refund 关联，以判断客户是否已经获得退款。案件结果由 Zip 决定；商家胜诉时 Stripe 会退回争议金额和费用，客户胜诉时扣款成为永久损失。

## 常见问题排查

**Zip 按钮不显示。** 检查商户和客户是否在同一个支持国家、货币是否本地匹配、购物车金额是否在方案范围、MCC 是否获批，以及动态支付方式使用的国家识别信息。

**客户能看到 Zip，但订单支付失败。** 查询 PaymentIntent、Stripe Webhook 和 Zip 授权结果，确认金额、币种和退回 URL。不要因用户回到网站就假设付款成功。

**美国客户问争议怎么提交。** 美国 Zip 争议由 Zip 管理，按其支持流程处理；确认该支付的实际国家和争议对象上下文。

**澳大利亚争议马上要到期。** 按 Dispute due_by 及时整理订单、发货、退货和沟通证据，在 12 天期限内提交。

**退款显示 pending。** Zip 正在异步处理。向客户说明通常需要数个工作日，并按国家解释退款是回原支付方式还是 Zip 余额。

## 上线检查清单

验证澳大利亚和美国的商户账户、消费者位置、币种、订单金额及各自方案展示。测试客户拒绝授权、返回成功页、重复 Webhook、全额与部分退款、退款失败、澳大利亚 dispute webhook 和美国客户争议指引。审查 Zip 的当地品牌要求、客户费用和融资条款表述，确保网站不会把一种国家的方案套用到另一国家。

Zip 集成的核心是按国家区分资格与售后处理。商户按订单获得付款，Zip 管理消费者分期；退款的资金返还地和争议响应渠道因国家而异。把国家、PaymentIntent、Refund 和 Dispute 关联起来，再由服务器事件驱动履约与对账，才能减少跨境误展示和退款误解。

## 官方资料

- [Stripe：Zip 支付](https://docs.stripe.com/payments/zip)
- [Stripe：Zip 收款接入](https://docs.stripe.com/payments/zip/accept-a-payment)
- [Stripe API：退款对象](https://docs.stripe.com/api/refunds/object)
- [Stripe API：Dispute 对象](https://docs.stripe.com/api/disputes/object)
- [Stripe：争议证据提交](https://docs.stripe.com/disputes/responding)
