---
title: "Stripe Alipay 支付接入与退款处理：币种、订单识别和对账"
date: 2026-11-15
description: "介绍 Stripe Alipay 的商户资格、顾客授权流程、支持币种、退款时限和交易编号对账，帮助面向中国消费者的业务规划钱包支付。"
slug: "stripe-alipay-payment-refund-currency-reconciliation-guide"
tags: [ "Alipay", "支付宝", "跨境支付"]
keywords: ["Stripe 支付宝接入", "Stripe Alipay 退款", "Alipay 交易编号对账", "Stripe Alipay 币种", "支付宝 Stripe 跨境收款"]
---

# Stripe Alipay 支付接入与退款处理：币种、订单识别和对账

面向中国消费者销售商品或服务时，Alipay 可以提供熟悉的钱包付款体验。Stripe 支持通过多个结账产品接入 Alipay，但它的商户资格、结算币种、可用 API 和退款流程都有边界。尤其要注意，Alipay 的支付授权发生在 Alipay 应用或网页中；客户返回商户网站并不应成为唯一的付款成功依据。

本文从商户资格、币种和产品支持讲起，再说明顾客授权、退款状态、交易编号和账务对账。官方支付方式的地区支持和功能可能更新，实际启用前应以 Dashboard 和 Stripe 当前文档为准。

## Alipay 的商户与客户范围

Stripe 文档将 Alipay 描述为面向中国客户的数字钱包。顾客可以在网页或移动设备上使用账户凭据或 Alipay 应用完成付款。商户账户所在地的支持范围比客户所在地更广；Stripe 当前文档列出多个北美、欧洲、亚太国家和地区的账户可以接受 Alipay，而使用 Alipay 的顾客所在地列为中国。

因此，不能只根据网站面向中国市场就假定账户必然可以启用 Alipay。商户还要满足 Stripe 和 Alipay 的业务类别要求，Stripe 可能在启用后对账户做资格复核。官方文档指出，商户网站需要公开可访问、不要求登录或跳转才能浏览，并清楚说明销售的产品或服务、价格、交付条款；如果经营代发货业务，也要披露。

上线前检查：

| 项目 | 核对内容 |
| --- | --- |
| Stripe 账户所在地 | 当前账户是否在 Alipay 支持的商户国家或地区 |
| 顾客所在地 | 产品是否主要服务中国消费者，业务场景是否适用 |
| 网站内容 | 产品、价格、交付和代发货说明是否可公开查看 |
| 业务类别 | 是否符合 Stripe 与 Alipay 的限制业务要求 |
| 账户状态 | Dashboard 是否已启用该支付方式，是否存在额外限制 |
| 交易币种 | 账户是否能以交易币种对应的方式进行结算 |

如果资格不明确，应先通过 Stripe 支持确认，而不是先在生产结账页向所有人展示 Alipay。账户支持、业务类别和支付集成类型三者都要匹配。

## 币种展示和结算要分别设计

Stripe 当前文档列出 Alipay 支持多个币种，包括 CNY、AUD、CAD、CHF、EUR、GBP、HKD、JPY、MYR、NZD、SGD 和 USD 等。商户账户需要具备与币种对应的银行账户或结算条件，具体哪些币种能用于某个商户账户，需参考 Stripe Dashboard 和账户实际配置。

Alipay 的默认本地币种为 CNY，客户也会看到以人民币展示的购买金额。页面上显示的币种、Alipay 授权时显示的金额以及 Stripe 账户的结算币种不是同一个概念。商户在商品页、订单确认邮件和客服页面中，应明确记录和展示最终订单币种与金额，并妥善处理货币换算和汇率说明。

如启用了多币种定价，建议按地区测试：

1. 中国客户打开商品页时，确认报价币种和最终订单币种。
2. 到结账页检查 Alipay 是否显示、金额和币种是否一致。
3. 在 Alipay 授权界面核对客户实际确认的金额。
4. 完成付款后，将 PaymentIntent 的金额、币种和 Charge 标识写入订单。
5. 将 Stripe 余额交易和银行结算数据用于财务对账，而非仅用前端页面金额。

还要检查最低和最高交易额。Stripe 文档当前列出 0.50 USD 的最低金额以及较高的最高金额，但具体可处理币种、地区、账户和支付场景应以实时配置为准。不要把此处限额直接当作商户产品定价规则。

## Alipay 授权与结账产品支持

Stripe 当前将 Checkout Sessions 列为推荐接入方式，也列出 Payment Links、托管发票页面和 Payment Element 等产品支持。并非所有 Stripe 产品或 API 都支持 Alipay。文档当前列明 Alipay 不支持一般订阅、Customer Portal、Terminal、In-app Payment Element、SetupIntent、off-session 支付，以及部分保存支付方式的使用方式。通过 Checkout 或 Hosted Invoice Page 创建的 Alipay 付款用于一次性支付。

如果产品使用 Checkout、Payment Links 或 Stripe 前端组件，先在 Dashboard 中启用 Alipay，再用测试模式验证目标地区和订单金额。Stripe 可以根据客户信息动态决定展示哪些支付方式。如果集成通过 API 手动指定 payment_method_types，服务器端必须确保当前账户、顾客地区、币种和交易场景符合要求。

顾客流程一般包括：

1. 在结账页选择 Alipay。
2. 移动端跳转到 Alipay 应用或移动网页；桌面端登录 Alipay，或使用应用扫描页面二维码。
3. 顾客检查金额和汇率，并在授权界面确认。
4. 顾客完成授权后返回商户网站或应用。

Stripe 文档说明顾客需要在限定时间内完成授权，当前流程描述为 5 分钟。用户离开结账页、取消支付、授权超时或浏览器未能返回，都不应让商户系统推断付款必然失败或成功。服务器要通过 Stripe 对象状态和事件同步最终结果，再决定是否履约。

## 用 Stripe 交易标识关联订单

每笔 Alipay 支付应保留一组稳定的关联标识：

- 内部订单号；
- PaymentIntent ID；
- Charge ID；
- Stripe Event ID（如果由 Webhook 触发）；
- Alipay 交易编号；
- 金额、币种和创建时间。

Stripe 文档说明，可以展开或检索 PaymentIntent 的 latest_charge，再从关联的支付方式详情中读取 Alipay transaction_id。这个编号适合用于与 Alipay 相关记录核对或协助客户定位交易。它不应取代 Stripe PaymentIntent 或内部订单 ID，因为业务系统需要同时关联商户订单、Stripe 支付对象和 Alipay 侧交易标识。

客户账单上显示的商户名称或交易描述也不完全由商户控制。Stripe 会把商户名称和订单描述等信息发送给 Alipay，Alipay 可能本地化、缩短、重新格式化或省略部分内容；客户关联的银行卡或资金来源账单显示方式也可能由 Alipay 和发卡方决定。因此不要向客户承诺银行账单一定逐字显示网站名称。若客户无法辨认交易，可以提供订单时间、金额和适当的 Alipay 交易信息协助核对。

## Alipay 退款时限和最终状态

Stripe 当前文档指出，Alipay 付款支持全额和部分退款，退款必须在原付款后的 90 天内提交。90 天是支付方式允许的最大提交窗口，不是商户面向客户的退货政策。退款流程异步进行，Stripe 文档当前描述最长处理时间为 5 分钟，而且退款不能取消。

Alipay 退款不是原支付的 reversal。退款会由 Alipay 直接处理并返还至客户原始付款来源，例如 Alipay 余额或绑定的支付方式。商户应以 Refund 对象的最终状态和 Stripe 通知更新订单，而不是仅根据 Refund 创建成功就认定客户已经收到款项。

推荐退款状态流：

| 状态 | 商户系统动作 |
| --- | --- |
| 退款请求已创建 | 保存 Refund ID、订单号、金额和原因 |
| 退款处理中 | 保持待处理状态，不对同一订单重复创建退款 |
| succeeded | 将该退款金额计入已退款金额并通知客户 |
| failed | 将任务交给客服或财务，安排替代处理 |

Stripe 可以通过 refund.updated 或 refund.failed Webhook 通知最终状态，也可以通过 Dashboard 或 Refund API 查询 Refund 对象。如果退款失败，Stripe 会把金额退回商户 Stripe 余额，商户需要使用替代方式向客户退款。站外退款要保留独立凭证，并关联回 Stripe 原始退款记录，防止系统把 Stripe 退款和替代退款重复计算。

退款流程还应区分“客户申请退款”“商户批准退款”“Stripe 创建 Refund”和“客户资金到账”这几个事件。客服可以说明已发起退款，但在 Stripe 状态确认前避免使用“已到账”表述。

## 没有标准争议流程意味着什么

Stripe 当前文档说明，Alipay 支付要求顾客在 Alipay 中直接认证，因此不支持标准的银行卡争议流程，顾客不能按卡组织流程发起 chargeback，商户余额也不会因这类争议被扣除。如果客户就某笔 Alipay 交易联系 Alipay，客户可能会被引导回商户，商户可以根据情况进行全额或部分退款。

这不意味着商户可以忽略售后义务，也不意味着所有客户投诉都会自动消失。应保留订单确认、商品交付、服务记录、退款政策和客户沟通，并为 Alipay 专门设置客服排查路径。与银行卡争议不同，这类场景可能更依赖商户与客户之间的订单核对和退款协商。

建议客服按照顺序核验：

1. 根据订单号、金额和日期定位 Stripe PaymentIntent。
2. 查看 Charge 是否关联 Alipay 支付方式及交易编号。
3. 确认订单是否已发货或服务是否已经提供。
4. 检查是否已有未完成 Refund，避免重复退款。
5. 如果同意退款，走 Stripe Dashboard 或 Refund API，并跟踪最终状态。
6. 记录客户联系原因、处理决定和凭证。

## Webhook 与日常对账

Webhook 接收端应验证 Stripe 签名，记录 Event ID，并对重复事件执行幂等处理。收到付款事件后，先按 PaymentIntent 或 Charge ID 找到订单，再更新订单状态。不要只依靠浏览器 return URL 触发履约。

对账任务至少核对：

- Stripe 付款是否成功；
- PaymentIntent 与 Charge 是否对应正确订单；
- Alipay transaction_id 是否保存；
- 原始支付金额和币种；
- Refund 对象当前状态；
- 退款成功金额与订单已退款金额是否相符；
- Stripe 余额变化和银行结算记录；
- 客服处理结果是否已同步到订单。

对于同一个订单有多笔退款时，应按每个 Refund 对象分别记录，并汇总已成功退款金额。对异步事件要允许重试和重复投递，避免同一退款多次累计。财务报告要把支付方式和币种记录完整，否则跨境收入和退款容易被错误归类。

## 上线检查清单

- [ ] Dashboard 确认账户已获准启用 Alipay。
- [ ] 官网公开展示产品、价格和交付条件。
- [ ] 商户业务类别符合 Stripe 和 Alipay 的要求。
- [ ] 顾客地区、交易币种和账户结算能力经过验证。
- [ ] 所选 Stripe 产品或 API 支持目标 Alipay 流程。
- [ ] 服务器端依据支付状态和 Webhook 确认订单，不依赖浏览器返回。
- [ ] 订单保存 PaymentIntent、Charge 和 Alipay transaction_id。
- [ ] 退款状态支持处理中、成功和失败三类结果。
- [ ] 退款失败会创建替代处理任务并保留凭证。
- [ ] 客服知道 Alipay 不使用标准银行卡 chargeback 流程，但仍要处理客户投诉和退款需求。

## 总结

Stripe Alipay 可以帮助符合资格的商户向中国客户提供钱包付款，但商户应先核对账户国家、网站信息、业务类别、币种和产品支持。支付完成依赖服务器端状态确认；退款要跟踪 Refund 对象最终结果；订单对账应同时保留 Stripe 对象 ID 与 Alipay 交易编号。

官方支持范围、币种、产品能力和退款时限可能调整。实际配置时请查看：

- [Stripe Alipay 支付文档](https://docs.stripe.com/payments/alipay)
- [Stripe Checkout](https://docs.stripe.com/payments/checkout)
- [Stripe Refund API](https://docs.stripe.com/api/refunds)
- [Stripe Webhook 签名验证](https://docs.stripe.com/webhooks/signature)
