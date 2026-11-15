---
title: "Stripe Checkout 一次性付款发票指南：invoice_creation、PDF 与邮件发送"
date: 2026-11-15
slug: "stripe-checkout-one-time-payment-paid-invoice-creation-guide"
description: "介绍如何为 Stripe Checkout 一次性付款启用付费发票，设置 invoice_creation、发票资料、成功付款事件和客户邮件。"
keywords:
  - Stripe Checkout 发票
  - invoice_creation enabled
  - Stripe 一次性付款 PDF 发票
  - paid invoice receipt
  - Stripe invoice.paid
tags:
  - Stripe
  - Checkout
  - 发票
  - 一次性付款
---

一次性付款成功后，客户可能需要一份列出商品、金额和商家信息的付费发票，而不仅是银行卡扣款回执。Stripe Checkout 可以在创建 Session 时启用购后发票生成功能，为成功的单次付款生成一张 paid invoice，并提供可下载的发票 PDF。这个选项适用于一次性购买，不等同于订阅账单或 Stripe Invoicing 的手动开票流程。

实现时，商家需要分别考虑三个环节：Checkout Session 是否创建发票、发票何时生成、Stripe 是否向客户发送邮件。打开 invoice_creation 负责创建发票；自动邮件则需要在 Dashboard 配置 Customer emails。对于延迟确认的支付方式，客户邮件和发票也要等待付款真正成功，不能在只提交了付款信息时就向客户承诺已付款。

## 什么情况下使用购后发票

适合的场景包括线上购买软件许可、一次性咨询服务、单次课程、设备订单或公司采购。客户付款后需要下载包含商品明细和商业信息的 PDF，商家希望减少人工整理回执的工作。Checkout 的购后发票会与相应付款关联，适合已收款后的凭证需求。

如果商家需要在收款之前向客户发送付款要求、设置到期日、进行催款或记录部分支付，应该评估 Stripe Invoicing 或其他发票流程。Checkout 的购后发票不是“先开票、再等待客户付款”的替代方案。Stripe 文档还指出，一次性付款的 Checkout 发票生成功能与 Invoicing 产品不是同一项功能，并可能按不同方式计费。上线前要查看当前 Stripe 价格和账户可用设置。

## 在 Checkout Session 中启用 invoice_creation

通过 Checkout Sessions API 创建一次性付款 Session 时，模式设置为 payment，并将 invoice_creation.enabled 设为 true。商品应使用服务器端可信的 Price ID、数量和订单数据；不要从浏览器直接接受金额作为最终收费依据。启用购后发票后，payment 模式 Session 会创建 Customer，因为生成发票需要客户对象。

可以将 invoice_creation.invoice_data 用于传递发票描述、页脚、custom_fields、metadata 等可配置资料。哪些字段能修改、哪些字段适用于特定账户或 API 版本，应以当前创建 Session API 文档为准。发票中显示的商家信息还与 Stripe 账户的公开业务资料相关，开启参数不会自动填充或验证所有法定信息。

Session 创建后，保存返回的 Session ID 和内部订单号。支付成功后，再从 Session 和发票对象中取回 Invoice ID、PDF 链接和 hosted invoice URL 等信息。客户可能在结账期间关闭浏览器，因此不要仅靠 success_url 执行发票保存或订单确认。

## 邮件发送和回执的区别

创建发票与给客户发送邮件是两件事。Stripe Dashboard 中的自动 Customer emails 设置控制成功付款和退款回执发送。若希望客户收到购后发票邮件，应按 Stripe 当前说明启用自动回执；对 Checkout Session，也可根据集成需要设置 receipt_email。成功付款后，Stripe 可以发送付款及发票摘要，并附发票和付款回执 PDF 的链接。

标准付款回执和逐项列出的付费发票也不是同一种文件。Stripe 会为成功付款生成回执，但默认并不一定给每位客户自动发送。Receipt URL 可以从 Charge 的 receipt_url 属性获取；发票则可从 Invoice 对象获取 invoice_pdf 或 hosted_invoice_url。商家可将这两个资料分别用于订单详情页面，避免在用户界面把一张普通卡片回执称作税务发票。

测试环境中的付款不会自动触发正式的收据邮件。如果需要验证客户收到的邮件，可依 Stripe 文档使用人工发送测试回执的流程。上线前还要检查账户的公开名称、客服邮箱、地址和税务资料是否符合发票展示要求。

## 延迟支付方式要等待异步确认

银行卡付款往往很快返回成功或失败，但银行转账、借记等方式可能需要更长时间确认。客户完成 Checkout 流程时，Session 可能已 complete，但付款状态仍可能是 unpaid 或 processing。发票的创建与邮件发送应遵循实际付款确认，不要因为用户跳转到成功页就把订单标成已付款。

对于延迟支付方式，Stripe 提供 checkout.session.async_payment_succeeded 和 checkout.session.async_payment_failed 等事件。商家应根据集成方式监听相应事件，并在服务端核实 Session、PaymentIntent 和 Invoice 状态。invoice.paid 事件可用于需要在程序中获取付费发票信息的场景。事件处理应验证 webhook 签名并做幂等，避免同一个付款重复触发发货、邮件或会计入账。

如果支付失败或被拒绝，不应把订单标记为已付款，也不应把尚未付款的文件作为付款凭证发送给客户。客户再次支付时应根据当前 Session 和支付状态创建新的支付流程，保留旧尝试便于客服和财务追踪。

## 发票资料与对账设计

在创建 Session 前，应核对商品名称、描述、税额、折扣和币种。结账页面上的项目描述应让客户理解自己购买了什么；invoice_data 的描述和页脚适合补充商家说明，但不能取代真实的商品行项目。客户的姓名、邮箱和账单地址也要根据产品及当地要求合理收集。

使用自动税时，应确保 Stripe Tax 的产品分类、商品价格税务行为、商家注册地和客户地址等设置正确。发票显示的税务明细取决于实际税务配置，不能仅通过修改 PDF 的说明文字来改变税务计算结果。法定发票要求因地区不同，商家需要根据当地要求核实格式和字段。

建议在内部数据库保存内部订单 ID、Checkout Session ID、PaymentIntent ID、Invoice ID、总金额、币种和当前状态。Invoice ID 可能在付款成功后才可从 Session 获取；发票 PDF URL 也可能涉及客户隐私，避免不加权限地暴露在公开页面。客服系统应通过已验证登录或订单访问凭证展示发票。

## 退款、部分退款和更正

付款退款不会自动意味着商家可以忽略原始发票或会计记录。退款后要把 Refund 与原付款和发票关联，保存退款金额、时间、状态和原因。需要对原发票进行会计更正时，使用适当的 Stripe 对象和会计流程，例如信用票据等，不能只删除发票 PDF 或覆盖订单金额。

如果部分退款，发票原始付款金额和退款金额应分别显示在订单记录中。客户可能需要原发票和退款凭证两份文件。退款事件和发票事件可能异步到达，因此要按事件 ID 去重，并在最终对账时从 Stripe 对象读取最新状态。

如果客户的电子邮件地址错误，先核实订单身份，再更新商家侧联系信息或通过 Stripe Dashboard 可用的收据发送功能重发。不要把含客户姓名、地址或税务编号的发票 URL 放入可以被搜索引擎索引的公开页面。

## 常见问题排查

**Checkout 完成了，却没有 Invoice ID。** 检查 Session 是否启用了 invoice_creation，是否是一次性 payment 模式，以及支付是否已经确认成功。也可从关联付款和 invoice.paid 事件核实。

**客户只收到普通回执。** 检查是否开启购后发票创建，并确认自动 Customer emails 配置。回执存在不等于付费发票也已创建。

**延迟付款后过早发货。** Session complete 与资金到账可能不是同一时刻。对延迟方式等待异步成功事件和服务端状态确认。

**Dashboard 出现 Customer 记录让人意外。** 购后发票需要关联客户资料，确认当前 Checkout Session 的 customer_creation 和 invoice_creation 设置符合预期。

**发票信息不完整。** 检查 Checkout 收集的客户资料、商家公开业务信息、商品价格、税务设置以及 invoice_data，而不是只查看订单成功页。

**退款后无法解释发票金额。** 将原始发票、付款、退款和可能的贷项调整放在同一个订单记录下，不要用退款金额改写原始付款记录。

## 上线前核对清单

- 仅在需要付款后逐项发票时启用 invoice_creation；
- Checkout Session 使用 payment 模式和可信的商品价格数据；
- 了解购后发票会关联 Customer，准备好客户资料映射；
- invoice_data 的描述、页脚、metadata 和自定义字段符合业务需求；
- Dashboard 自动回执设置与客户通知预期一致；
- Stripe 账户的公开商家信息和税务资料已核对；
- 监听成功付款、异步付款和 invoice.paid 事件；
- 订单仅在服务端确认付款后交付商品；
- 发票 PDF 和 hosted URL 只向已授权客户展示；
- 退款和部分退款流程保留原发票及调整记录；
- 测试正式支付和延迟确认支付方式的全生命周期。

## 总结

Stripe Checkout 的 invoice_creation 可为一次性付款生成购后付费发票，但它不是订阅账单，也不是先开票后收款的完整 Invoicing 流程。开启后要将发票与 Customer、付款和内部订单建立清晰关系，并分别确认发票生成与邮件发送设置。

使用 webhook 和服务端对象状态处理付款结果，尤其要为延迟支付方式等待异步确认。上线前校验商品行、税务资料、客户信息、PDF 权限和退款更正流程，能减少客户收据混淆和财务对账问题。

## 参考资料

- [Stripe：收据和付费发票](https://docs.stripe.com/receipts)
- [Stripe API：创建 Checkout Session](https://docs.stripe.com/api/checkout/sessions/create)
- [Stripe：Checkout 付款完成处理](https://docs.stripe.com/checkout/fulfillment)
- [Stripe API：Invoice 对象](https://docs.stripe.com/api/invoices/object)
