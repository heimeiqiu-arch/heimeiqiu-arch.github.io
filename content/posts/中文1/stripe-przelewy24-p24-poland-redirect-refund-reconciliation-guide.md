---
title: "Stripe Przelewy24 接入指南：波兰银行跳转、付款确认与退款"
date: 2026-11-15
slug: "stripe-przelewy24-p24-poland-redirect-refund-reconciliation-guide"
description: "Stripe Przelewy24（P24）如何面向波兰客户收款，处理银行跳转、付款与退款 Webhook，并核对 PLN/EUR、一次性支付限制和商户资格。"
keywords:
  - Stripe Przelewy24
  - Stripe P24 波兰支付
  - P24 退款
  - Stripe Przelewy24 接入
  - Stripe refund.failed
tags:
  - Stripe
  - 支付方式
  - 波兰
---

向波兰消费者销售时，Przelewy24（常简称 P24）让客户通过本地银行转账和其他方式完成线上付款。Stripe 将 P24 作为银行重定向类支付方式接入：客户选择 P24 后跳转到 P24 页面，选择银行并授权付款，再返回商家网站。与银行卡付款相比，退款和结算时序不同；若系统只在付款成功页发货，或把 P24 当作可保存的周期扣款方式，容易造成订单状态错误。

本文整理 Stripe P24 的市场适用、Checkout 与 Payment Element 的接入、重定向与付款确认、异步退款、银行账单参考号以及对账方法。Stripe 对 P24 的业务资格、行业限制、币种和功能可能调整；上线前需要检查当前 Dashboard 和 Stripe 官方说明。

## 哪些客户可以使用 P24

P24 面向波兰客户，支付页面可展示 PLN 或 EUR。Stripe 当前文档列出 0.50 EUR 的最低金额。商户账户必须具备对应支付方式资格；账户位于可接受 P24 的国家，不代表所有行业和商业模式都自动通过审核。Stripe 对某些 MCC 和业务类别有禁止或限制要求，商户应核对完整清单，并在网站展示经营地址、税务和注册信息、退款政策、隐私政策及服务条款等适用资料。

客户所在国家是波兰，和 Stripe 商户账户所在国家是两个独立条件。结账时应根据产品目标市场、账户资格、结账币种和客户所在地区决定是否展示 P24。使用动态支付方式时，让 Stripe 根据配置和上下文选择相关方式；手动枚举支付方式时，则需自行管理资格和币种匹配，避免向不适用客户展示后才报错。

P24 是一次性支付方式，不支持 recurring payments、off-session 扣款、保存支付凭证供后续扣款、手动捕获或部分捕获。它不适合直接作为自动续费订阅的付款方式。如果产品需要订阅，应选择支持后续扣款的支付方式；P24 可用于一次性购买，或在仅适用的发送发票模式下按 Stripe 支持范围配置。

## 客户重定向与付款确认

典型流程是客户在结账页选择 P24、跳转到 P24 选择银行、完成授权，然后返回商家网站。客户通常需要在 Checkout 开始后一小时内完成授权。Stripe 文档说明 P24 付款确认较快，但你的系统仍应按服务端 PaymentIntent 或 Checkout Session 状态确认交易，而不应只依据客户是否被重定向回来。

浏览器跳转无法保证一定完成：客户可能关闭页面、网络断开、跳转被浏览器拦截或返回页面加载失败。网站成功页可以用来展示订单进展，但履约应由 Stripe Webhook 或后端查询结果触发。Checkout 集成可以监听 checkout.session.completed，并根据订单金额、币种、支付状态及内部订单关联校验后再履约。PaymentIntent 集成则检查 PaymentIntent 的最终状态与相关 Charge。

Webhook 接收端先验证签名，再按 Event ID 去重。将 Checkout Session ID 或 PaymentIntent ID 和内部订单主键绑定，事件到达时重新读取必要的 Stripe 对象，并核对真实金额和货币。不要信任浏览器提交的订单总价，也不要因为同一事件被 Stripe 重试就重复发货或开通数字服务。

## 退款是异步的银行入账

P24 支持全额和部分退款。Stripe 当前文档说明，原付款后最多 180 天内可以通过 Dashboard 或 Refunds API 提交；这只是支付方式允许的最长期限，不代表商家的退款政策必须覆盖整个期限。企业仍需依据产品条件、合同和适用规则确定对客户提供的退款承诺。

提交 P24 退款后，处理是异步的，通常最多需要三个工作日，而且提交后不能取消。退款是单独入账到客户银行账户，不是卡片交易的撤销。银行账单上的退款不会清楚标注为退款，而会显示一笔关联原交易描述的贷记。因此建议商家主动发送退款通知，说明金额、提交日和 Stripe 退款参考号（如有），帮助客户辨认入账。

退款创建成功不等于退款最终成功。保存 Refund ID，监听 refund.updated 或 refund.failed，并读取 Refund 对象 status。若状态成功，可在退款记录中保存 reference；若状态失败，Stripe 会将金额退回 Stripe 余额，商家需要与客户安排另一种退款方式。失败后不要盲目再次发起同一笔 P24 退款，应先核对 Stripe 对象和余额变化，再决定如何结案。

## 银行账单参考和客服查询

客户询问“这笔扣款是什么”时，商家可以通过 P24 交易参考号帮助客户识别银行账单。Stripe 文档说明，可在支付完成后展开 PaymentIntent 的 latest_charge，并读取 latest_charge.payment_method_details.p24.reference（具体字段应以当前 API 对象为准）。PaymentIntent 确认前设置的 statement descriptor 会影响银行账单的描述；对于 Connect，也要按 connected account 和平台的描述规则核实。

客服系统应优先按内部订单号、Checkout Session ID、PaymentIntent ID、Stripe Customer ID 或交易时间金额查找付款。将 P24 参考号安全地记录在付款详情中，便于解释银行账单；不要仅靠客户转述的银行流水描述匹配交易，因为不同银行的显示格式可能不同。

## Connect 平台接入注意

平台商户也可以评估 P24，但应检查每个 connected account 的资格和能力。Stripe 文档说明，某些使用 Express Dashboard 或没有 Stripe 托管 Dashboard 的 connected account，需要申请 p24_payments capability，并确认状态为 active 后才接受 P24 付款。平台自身账户已启用 P24，不代表每个连接账户都拥有相同支付能力。

在平台订单模型中分别保存顾客支付、平台转账和 connected account payout 信息。P24 付款成功后进入 Stripe 余额与结算的过程，和银行退款返还过程不是同一个对象。平台在资金对账中应按 PaymentIntent、Charge、Refund、Balance Transaction 和账户上下文关联，避免把一笔退款误记为 payout 失败或将平台账户和 connected account 的交易混在一起。

## 常见问题排查

**结账页没有 P24。** 检查付款客户是否为波兰客户、交易币种、账户资格、Dashboard 是否启用、网站业务信息是否满足要求，以及是否受到行业限制。手动 payment_method_types 配置也可能意外排除了 P24。

**客户完成银行授权，但订单仍是待付款。** 按 PaymentIntent 或 Checkout Session ID 读取最新状态，检查 Webhook 投递记录和事件处理日志。浏览器跳转只说明客户返回，不应作为付款最终成功的唯一依据。

**想让 P24 自动续费。** P24 不支持 recurring 或 off-session payment。改用支持后续扣款的方式，或将 P24 限制为一次性付款。

**客户说退款没有到账。** 查询 Refund 状态与事件；向客户说明银行处理时间通常为数个工作日，并提供 Stripe reference（若存在）。若退款为 failed，按替代退款流程处理。

**银行账单没有“退款”字样。** P24 退款可能作为独立贷记显示，描述可能关联原支付。通知客户查询同等金额的入账，并提供参考号和提交日期。

## 上线验证清单

测试 P24 支付成功和客户中途离开；验证 Webhook 重复投递、订单已支付但页面未返回、部分退款、退款延迟和退款失败。确认 PLN/EUR 显示、商户资格、Connect capability、银行账单描述和客服查单方式均符合实际。核对不支持的 recurring、off-session 和手动捕获场景没有被产品流程承诺。

P24 的集成重点是把银行跳转、一次性付款和异步退款拆开管理。后端以 Stripe 状态驱动履约，退款用 Refund 对象与 Webhook跟踪，银行参考号用于客服和对账。明确这些边界，可以帮助波兰客户顺利付款，也能让财务团队在退款尚未到银行时准确解释进展。

## 官方资料

- [Stripe：Przelewy24 支付](https://docs.stripe.com/payments/p24)
- [Stripe：P24 收款接入](https://docs.stripe.com/payments/p24/accept-a-payment)
- [Stripe API：创建退款](https://docs.stripe.com/api/refunds/create)
- [Stripe API：退款对象](https://docs.stripe.com/api/refunds/object)
- [Stripe：Checkout 履约](https://docs.stripe.com/checkout/fulfillment)
