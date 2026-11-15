---
title: "Stripe Multibanco 葡萄牙支付凭证：七天有效期、延迟入账与退款"
date: 2026-11-15
slug: "stripe-multibanco-portugal-voucher-expiry-delayed-payment-refund-guide"
description: "Stripe Multibanco 如何处理葡萄牙客户银行凭证、EUR 金额、七天到期、过期后 processing 状态、异步履约和 456 天退款窗口。"
keywords:
  - Stripe Multibanco
  - Multibanco 葡萄牙支付
  - Multibanco payment voucher
  - Stripe Multibanco 退款
  - PaymentIntent processing Multibanco
tags:
  - Stripe
  - 支付方式
  - 葡萄牙
---

Multibanco 是葡萄牙广泛使用的支付方式。客户在 Stripe Checkout 选择 Multibanco 后，会拿到包含实体编号、参考号、金额和有效期的付款凭证，再通过网上银行或 ATM 付款。它不是即时银行卡支付：客户付款后不会自动跳回商家网站，Stripe 可能需要几天才收到最终付款确认。若把“凭证已生成”当作“收款成功”，很容易提前发货或错误开通服务。

Multibanco 还有较长的退款提交窗口，但退款到客户银行账户的时间仍需按 Refund 状态和银行进度核对。本文说明凭证有效期、订单状态、延迟确认、发票限制、退款和 Connect 能力。国家资格、货币和支付方式支持会变化，请在 Dashboard 和当前 Stripe 文档中核实账户状态。

## 适用客户、账户和金额

Multibanco 主要面向葡萄牙客户，展示币种为 EUR。Stripe 当前列出的单笔金额范围为 0.50 至 99,999 EUR。商户账户可以来自文档列出的一些欧洲国家和美国，但客户使用地区以葡萄牙为主；账户还需通过支付方式审核，具体业务类别要符合 Stripe 的规则。

它是一次性付款方式，不支持 recurring、off-session 自动扣款或保存为未来支付凭证。Billing 和 Invoice 只有在 collection_method=send_invoice 的情况下适用于相关场景，客户仍需每次主动付款。不能把一次 Multibanco 付款转换为自动续费授权。

平台使用 Connect 时要确认 connected account 的账户能力和交易模型。使用 Express Dashboard 或没有 Stripe 托管 Dashboard 的连接账户，可能需要申请 multibanco_payments capability，并确认其状态为 active。平台本身可用不等于每个 connected account 都自动可用。

## 七天凭证与客户支付步骤

客户在结账时选择 Multibanco 并提供邮箱。Stripe 展示实体编号、参考号、金额和到期时间；凭证默认在创建后七天过期。商家可以按集成方式设置 Stripe 向客户发送凭证邮件，避免用户离开页面后找不到付款信息。

客户使用凭证信息通过网上银行或 ATM 转账。PaymentIntent 在等待付款时可能处于 requires_action。客户完成支付后不会自动重定向回商家网站，因此商品履约不能依赖 return URL。系统应把订单状态标记为“等待银行付款”，并说明客户需要在到期前按凭证的金额和参考信息付款。

到期后，支付通知仍可能延迟。Stripe 文档说明，凭证过期后 PaymentIntent 可能继续处于 processing 状态最多四天，等待延迟付款通知。不能因为凭证过期就立即删除所有订单记录或向同一订单再次创建可付款凭证；先检查 PaymentIntent 最新状态，以免客户在有效期末支付后出现旧款成功、新款也被付款的重复收款。

## Webhook 驱动异步履约

Multibanco 付款状态应由服务端 PaymentIntent 和 Webhook 同步。创建凭证仅表示客户拥有付款说明；只有 Stripe 将 PaymentIntent 变成 succeeded，才可以按业务规则确认收款并履约。Webhook 接收端要验证 Stripe 签名、记录 Event ID，并对支付成功后的库存扣减、物流、发票和邮件操作实现幂等。

建议保存内部订单号、PaymentIntent ID、客户邮箱、金额、币种、实体编号、付款参考号、到期时间和最后状态更新时间。Webhook 到达后校验订单关系、金额和币种，确认同一订单没有其他成功付款，再创建履约任务。若系统因暂时故障没有及时处理成功事件，可以安全重放履约逻辑，但需先检查订单是否已经发货。

如果客户发邮件说已经转账但系统仍显示 processing，客服先核对凭证参考号、转账时间和金额，并查看 Stripe 事件状态。不能仅凭客户截图把未确认的 PaymentIntent 改成 succeeded。必要时通过 Stripe 支持或内部财务流程核查，不要丢弃 PaymentIntent 以免延迟通知到达后无法匹配。

## 退款时间窗与状态管理

Stripe 当前文档说明，Multibanco 付款在原交易后 456 天内可申请全额或部分退款。这个期限是支付方式可提交退款的技术窗口，不替代商家的退货政策。退款直接发送到客户银行账户，通常约一天到账，但时间依银行而异；提交后不能取消。

退款完成依赖 Refund 对象状态。监听 refund.updated 和 refund.failed，或在 Dashboard/API 查询。状态 succeeded 后保存退款完成信息；失败时 Stripe 会将退款金额退回 Stripe 余额，商家需要以其他方式退还客户。客服通知中包括金额、原订单、退款发起时间和参考号（若对象提供），不要只说“已经发起”就把问题标记为结案。

部分退款要累计计算并确保总退款金额不超过原始付款金额。每个 Refund ID 与 PaymentIntent 关联，保留退款原因和审核人。若多次退款请求并发提交，可在内部对订单加锁或用唯一约束，避免两名客服同时对同一笔付款超额退款。

## 对账与银行参考号

Multibanco 的实体编号和参考号用于客户付款说明，和付款成功后 Stripe 的 Balance Transaction 不是同一概念。财务记录中保存 PaymentIntent、Charge（适用时）、余额交易、Refund 和 payout ID，按 EUR 金额、订单号和付款日期核对。客户银行到账和 Stripe 余额可用也不是一回事，Payout 还受商户账户的打款日程影响。

Statement descriptor 可能显示在客户银行流水中，具体样式因银行而异。支付级 descriptor 可帮助客户辨认交易，但 Connect charge type 会决定平台还是 connected account 的描述被使用。对账时优先按 Stripe 对象 ID 与凭证参考关联，不要仅靠客户看到的文字匹配。

## 常见问题排查

**Checkout 显示 completed，但订单不能发货。** 查看 PaymentIntent。对于 Multibanco，Session 完成只说明结账和凭证创建流程完成，收款仍可能待确认。

**凭证过期，状态仍是 processing。** 这是等待延迟付款通知时可能出现的状态。按 Stripe 文档和具体对象继续观察，避免立刻重复创建同一订单付款。

**客户付款后没有返回网站。** 这是正常情况。通过 Webhook 和 PaymentIntent 状态更新订单，不要依赖客户浏览器返回。

**退款已发起但客户尚未收到。** 检查 Refund 状态和银行处理时间；通常约一天但银行可能不同。退款失败时按其他方式退款。

**商户希望用 Multibanco 自动续费。** Multibanco 不支持自动扣款。使用支持重复支付的方式，或采用需客户主动支付的 send_invoice 方案（如适用）。

## 上线前检查清单

验证 Checkout 生成凭证、客户收取邮件、七天过期、网上银行或 ATM 付款后事件延迟、到期后 processing、PaymentIntent 成功触发履约、Webhook 重放、退款全额与部分退款、退款失败和 Connect capability。检查 EUR 金额边界、账户资格、发票收款方式和客服能否查到凭证信息。

Multibanco 的集成关键在于凭证创建与实际到账之间可能间隔数日。将订单先置于待银行支付状态，等待 Stripe PaymentIntent succeeded 后才履约；对凭证过期后的 processing 继续核查；退款则按 Refund 对象最终状态管理。这样既能支持葡萄牙本地银行付款，又能避免重复订单和未收款发货。

## 官方资料

- [Stripe：Multibanco 支付](https://docs.stripe.com/payments/multibanco)
- [Stripe：Multibanco 收款接入](https://docs.stripe.com/payments/multibanco/accept-a-payment)
- [Stripe API：PaymentIntent 对象](https://docs.stripe.com/api/payment_intents/object)
- [Stripe API：Refund 对象](https://docs.stripe.com/api/refunds/object)
- [Stripe Connect：账户能力](https://docs.stripe.com/connect/account-capabilities)
