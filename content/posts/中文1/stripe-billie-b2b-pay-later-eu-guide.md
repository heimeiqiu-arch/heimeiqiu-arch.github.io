---
title: "Stripe Billie B2B 账期付款指南：30 天付款、退款和争议处理"
date: 2026-11-15
slug: "stripe-billie-b2b-pay-later-eu-guide"
description: "介绍 Stripe Billie 面向欧洲企业买家的 B2B 30 天账期支付，覆盖国家、币种、Stripe Checkout 限制、365 天退款窗口和争议证据期限。"
keywords:
  - Stripe Billie
  - Billie B2B 30天付款
  - Stripe 企业先买后付
  - Billie 退款和争议
  - Billie Connect capability
tags:
  - Billie
  - B2B支付
  - 先买后付
---

Billie 是面向企业买家的先买后付方式。买家在结账时选择 Billie，跳转到 Billie 页面提供信息并授权 30 天付款条款；商家则由 Stripe 在客户授权后收到款项，不需要自己等待企业账期结束。它适合企业采购、批发和 B2B 电商，不能被当成一般面向消费者的 BNPL，也不是商家自建的延期付款合同。

Stripe 与 Billie 的组合提供即时付款确认，但业务仍需要处理授权失败、退款、争议和连接账户资格。商家在启用前，应核对 Billie 允许的国家、币种、业务类别及交易金额，并检查 Checkout 的产品限制。特别是 Billie 不支持订阅、off-session 付款或 Checkout subscription 模式；企业客户的“30 天付款”由 Billie 管理，不等于商家可以把这项支付方式用于循环扣款。

## 商家和客户资格

Stripe 当前文档列出的商家账户地点和客户地点包括奥地利、瑞士、德国、丹麦、西班牙、芬兰、法国、英国、荷兰、挪威和瑞典。Billie 的业务模式面向 B2B，不支持 B2C。商家应在服务端确认购物车属于企业订单，并按 Billie 流程收集所需的公司信息；不能因为买家填写了公司名称就假设其已通过 Billie 授信。

支持的展示币种为 CHF、DKK、EUR、GBP、NOK 和 SEK。账户国家与可用于结算的币种有组合限制，例如 GBP 对应英国账户，CHF 对应瑞士账户；其他币种也需符合当前文档列出的国家范围。单笔最低金额为 0.01 EUR 等值，但最高金额按国家和币种变化。最终可用金额应以 Stripe API 和 Billie 结账页面的实际结果为准，不要在产品页面写一个所有欧洲市场通用的上限。

Billie 对某些业务类别和 MCC 有禁止或受限规则，包括金融机构、加密货币交易、赌博及部分建筑服务等。具体清单可能更新，商家应在 Dashboard 和 Stripe 官方 MobilePay/Billie 页面核对自己的 MCC 与商品类型。若行业属于受限类别，提前确认是否需要提交额外账户材料。

## 客户付款与订单状态

在 Stripe Checkout 或 Payment Element 中启用 Billie 后，符合条件的 B2B 客户可以选择该付款方式。Stripe 将客户重定向至 Billie，买家授权账期并返回商家网站。Stripe 会及时通知付款成功或失败。用户回到网站本身不是支付证据，订单系统应通过 Webhook 或服务端读取 PaymentIntent 状态再安排履约。

建议将企业订单记录与支付尝试关联，保存 Checkout Session ID、PaymentIntent ID、公司客户编号、最终金额和币种。通过 Billie 付款成功后，可以从 PaymentIntent 的 latest_charge.payment_method_details.billie.transaction_id 获取 Billie 交易编号。客户就付款条件联系 Billie 时，这个交易编号可能有助于客服与账款查询。

Billie 提供的是一次性支付，不能保存为未来离线付款方式。若客户需要每月订阅或定期收费，应选择支持 recurring 的其他方式。Billie 支持 Stripe Billing 和 Invoicing 的特定情形，但官方说明仅支持 send_invoice 收款方式；Checkout 不支持 subscription 或 setup 模式。设计 B2B 发票流程时，要将单笔账期付款与订阅自动扣费分开。

## 退款：提交窗口与异步状态

Billie 要求退款在原始付款后 365 天内提交，这是该支付方式允许的最长时间，不代表商家必须在一年内接受任何退货申请。退款权利仍取决于商家的销售条款和适用法律。Stripe 支持全额和部分退款，可以通过 Dashboard 或 Refunds API 操作。Billie 的退款是异步处理，通常最多约 5 分钟完成，退款提交后不能取消。

退款会同步调整 Billie 客户的付款义务。全额退款会取消剩余账期付款；部分退款会把客户应付金额调整为较低的订单余额。商家在创建退款时应核对原付款、累计退款金额和订单行项目，不要在内部数据库先把退款标为成功。通过 refund.updated 或 refund.failed Webhook 获取最终状态，并验证签名和去重事件。

若 Refund 对象最终为 failed，Stripe 会把金额退回商家 Stripe 余额，商家需要使用其他方式向客户退款。客服要说明替代退款方式和处理进度，并将外部退款凭证与 Stripe 原订单关联。由于退款提交后不能取消，提交前要检查客户、币种、金额及退款去向。

## 争议和证据期限

Billie 客户从购买日算起最多 365 天可以提出争议。争议创建后，Stripe 会立即从商家余额暂扣争议金额，商家有 35 个日历日提交证据。Billie 在证据提交后七个日历日内作出最终决定。商家要以 Dashboard 中的截止日期和 Dispute 对象 evidence_details.due_by 为准，不能把 35 天误认为 35 个工作日。

收到 charge.dispute.created 后，应立即收集订单、发货和交付记录、客户沟通、售后记录，以及已经退款时的退款证明。可以通过 Dashboard 或 Disputes API 提交证据；API 方式需要先通过 Files API 上传附件，再把文件 ID 加入争议证据。赢得争议时 Stripe 会返还争议金额，若裁决支持客户，余额扣款会成为最终损失。

由于证据期相对明确，建议由后台任务提醒客服、财务和履约团队在期限前准备材料。保留公司下单主体、采购订单号、送货地址、运输追踪和签收信息，可帮助处理 B2B 采购争议。不要只凭客户声称未收到付款邮件就重复发货或再创建一笔同金额交易。

## Connect 平台接入

Stripe 文档支持 Billie 用于 Connect 平台或 Marketplace，但平台账户和希望启用 Billie 的 connected account 都需要 billie_payments capability 处于 active。平台要按每个卖家检查能力状态，并根据付款失败或能力尚未就绪的情况隐藏或替换 Billie 选项。

商家名称和账单描述受 Connect charge 类型影响。Direct charge 通常采用 connected account 的描述，destination charge 通常采用平台描述；使用 on_behalf_of 时，描述归属可能不同。平台应检查客户在银行应用和确认邮件中看到的商户名称、对账字段、退款责任和争议处理路径。不要仅因为平台能接受 Billie，就认为所有 connected account 已自动满足资格。

## 上线前检查清单

- 订单属于企业对企业，不将 Billie 展示给 B2C 买家；
- 商家与客户国家属于当前支持范围；
- 结算账户和交易币种组合符合 Stripe 文档；
- 交易金额达到最低值且未超过该地区的实际上限；
- MCC 和行业类别没有被禁止或限制；
- Checkout 使用 payment 模式，不在订阅或 setup 模式启用；
- Billing 或 Invoicing 场景使用支持的 send_invoice 流程；
- 以服务端状态和 Webhook 确认付款后履约；
- 退款在 365 天窗口内提交，并等待异步最终状态；
- 退款失败时有替代退款方式和客服流程；
- 争议有 35 个日历日证据提醒和材料留存；
- Connect 平台与 connected account 的 capability 均已激活。

## 常见错误

**把 Billie 当作消费者分期。** Stripe 集成面向企业买家，B2C 不受支持。

**Checkout 配成订阅付款。** Billie 不支持 Checkout subscription 或 setup 模式，也不支持 recurring 和 off-session 扣款。

**把 Stripe 收款到账和客户付款账期混为一谈。** 商家收到款项后，客户仍按 Billie 与其约定的付款条件处理。

**超出退款窗口或误以为可撤回退款。** 最晚在原始付款后 365 天提交，提交后不能取消。

**等到争议截止日前才开始收集证据。** 争议开放后证据期为 35 个日历日，应及时收集订单和交付记录。

**只在平台账户申请 capability。** Connect 还要检查平台和具体 connected account 的 billie_payments 状态。

## 总结

Stripe Billie 允许合格地区的企业买家选择 30 天付款条款，而商家在 Billie 授权后即可由 Stripe 收到款项。该方式支持 EUR、GBP、CHF、DKK、NOK 和 SEK 等币种，但账户国家、客户地点和币种组合存在限制，B2B 资格与 MCC 也需要审核。

Billie 是单次付款，不支持 recurring、off-session 或 Checkout subscription/setup。退款需在 365 天内提交且异步处理；争议通常给商家 35 个日历日提交证据。把 Billie 用于合适的企业订单，并为退款和争议建立后台流程，才能减少账期付款后的运营遗漏。

## 参考资料

- [Stripe：Billie 支付方式说明](https://docs.stripe.com/payments/billie)
- [Stripe：Billie Checkout 接入](https://docs.stripe.com/payments/billie/accept-a-payment)
- [Stripe：争议证据提交](https://docs.stripe.com/disputes/responding)
- [Stripe API：退款对象](https://docs.stripe.com/api/refunds/object)
