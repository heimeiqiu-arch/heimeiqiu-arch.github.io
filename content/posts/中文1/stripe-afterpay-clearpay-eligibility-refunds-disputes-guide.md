---
title: "Stripe Afterpay 与 Clearpay 接入指南：地区资格、退款和争议对账"
date: 2026-11-15
description: "说明 Stripe Afterpay/Clearpay 的国家与币种限制、结账跳转、订单确认、退款跟踪和争议证据时限，帮助商户规划分期付款流程。"
slug: "stripe-afterpay-clearpay-eligibility-refunds-disputes-guide"
tags: ["Stripe", "Afterpay", "Clearpay", "分期付款"]
keywords: ["Stripe Afterpay 接入", "Clearpay Stripe", "Afterpay 退款", "Afterpay 争议处理", "Stripe 分期付款"]
---

# Stripe Afterpay 与 Clearpay 接入指南：地区资格、退款和争议对账

Afterpay 是一种先买后付支付方式，在英国以 Clearpay 的名称面向消费者。顾客在结账时跳转至 Afterpay 登录或创建账户、选择分期方案并授权，之后由 Afterpay 按其计划向顾客收款。商户侧通过 Stripe 处理支付接入和交易状态，支付完成后仍需处理订单履约、退款和争议。

接入前最容易忽略的是可用地区和产品支持边界。Afterpay 并不适用于所有商户、所有国家或所有 Stripe 产品。即便结账组件可以展示分期选项，具体交易仍可能受顾客国家、币种、金额、商户类别和 Afterpay 授权结果影响。本文围绕资格确认、结账配置、履约确认、退款和争议处理整理一套运营流程。

## 确认商户、顾客和订单符合条件

Stripe 官方文档列出的 Afterpay 商户账户所在地包括澳大利亚、加拿大、英国、新西兰和美国；顾客所在地和可用币种也与国家对应。一般可用范围内仅支持国内交易，跨境支付仍处于特定预览范围。使用动态支付方式时，Stripe 会根据客户资格筛选可展示的支付方式；如果集成手动指定 payment_method_types，商户就要自行确保仅向符合条件的客户显示 Afterpay。

交易金额也会因国家和币种不同而不同。文档示例列出澳元、加元、英镑、新西兰元和美元的对应限额，并指出美国支持 Pay in 4 和部分月付方案。金额范围和业务资格可能变化，务必在启用当天检查 Payment methods 设置和官方支付方式页面，不要把一组国家或金额限制硬编码为永久规则。

接入前先核对以下项目：

| 核对项 | 为什么要确认 |
| --- | --- |
| Stripe 账户国家 | 决定商户是否可能启用 Afterpay 及可用结算方式 |
| 顾客所在国家 | 决定结账是否应展示 Afterpay |
| 币种和订单金额 | 不同国家方案和最低、最高金额可能不同 |
| 商户类别 | 某些业务类别被禁止使用，另一些可能需要额外资料 |
| 业务模型 | Stripe 当前文档将此支付方式定位为面向消费者的购买场景，B2B 不支持 |
| 产品和 API | Billing、Invoicing 等部分产品/API 不支持 Afterpay，具体以官方支持表为准 |

某些类别，例如酒类、捐赠、预售、NFT 和 B2B，在 Stripe 文档中列为禁止使用 Afterpay 的业务。部分 MCC 则属于限制类别，可能要补充资料。由于资格列表会更新，应把 Stripe Dashboard 的支付方式页面作为账户当前状态的首要检查入口。

## 选择适合的 Stripe 结账产品

Stripe 当前文档列出 Afterpay 对 Checkout Sessions、Payment Intents、Payment Links、Payment Element 和嵌入式结账等部分流程的支持，同时明确列出不支持的产品与能力，包括订阅、发票、Customer Portal、Radar、Terminal、离线付款及将 Afterpay 保存为未来使用的部分场景。不要仅因为 PaymentIntent 可以展示某种支付方式，就推断它能用于订阅或后续免交互扣款。

对于新接入，Stripe 将 Checkout Sessions 列为推荐 API。使用 Checkout、Payment Links 或 Payment Element 时，先根据业务所需定制程度选择产品，再核对其当前支持矩阵。产品能力、地区资格和支付方式能力是三个不同层面，缺一项都可能导致结账行为与预期不同。

若手动列出支付方式，需要在服务器创建支付对象时确保 Afterpay 只在适用条件下开放。若使用动态支付方式，仍要在测试环境验证地区识别、订单金额、币种和顾客页面结果。Stripe 文档说明动态支付方式可依顾客资格决定是否显示 Afterpay；这有助于减少客户端自行维护地域规则的工作，但不能代替商户对账户资格的检查。

## 理解顾客跳转和付款确认

Afterpay 的顾客流程通常包含以下步骤：

1. 顾客在结账页面选择 Afterpay。
2. 桌面设备跳转到 Afterpay 页面；移动设备可能打开 Afterpay 应用，若未安装则打开网站。
3. 顾客登录或创建账户，选择分期计划并同意还款条款。
4. 完成授权后返回商户结账页，商户端继续处理订单状态。

顾客在 Afterpay 中选择方案的授权时限有限，Stripe 当前文档说明为 3 小时。订单系统应将“用户离开结账页”“正在授权”和“付款已确认”分开处理，避免顾客跳转回来就默认订单已成功。付款是否已成功应依据 Stripe 支付对象状态以及服务器端收到的事件，而不是只依赖前端 return URL。

对一次性订单，成功支付后再发货或交付数字内容。付款失败、顾客取消或授权超时，则保留失败原因并允许顾客回到结账流程重新尝试。支付和履约要使用内部订单号与 Stripe 对象 ID 关联，减少客服在多个系统之间手工匹配。

## 退款期限、异步结果和客户沟通

Stripe 文档指出，Afterpay 全额和部分退款都需要在原始交易后的 120 天内提交，退款处理是异步的，最长可能需要 10 个工作日。Afterpay 退款不能取消，也不会作为撤销原交易的 reversal 处理。Afterpay 会取消尚未到期的分期，并返还顾客已经支付的金额。

因此，商户不应把“退款请求创建成功”当成“顾客已收到退款”。应记录 Stripe Refund 对象 ID、退款金额、提交时间和最终状态，并通过 Dashboard、Refund API 或 Webhook 跟进结果。Stripe 文档指出，退款状态最终变化会通过 refund.updated 或 refund.failed 事件通知。

建议把退款状态分成三个阶段：

| 内部状态 | 业务处理 |
| --- | --- |
| 退款请求已提交 | 保存退款对象与关联订单，告知顾客已发起处理 |
| 退款处理中 | 继续等待 Stripe/Afterpay 更新，不重复创建同金额退款 |
| 退款成功或失败 | 成功后更新已退款金额；失败后建立人工处理任务 |

退款失败时，Stripe 会把金额返还到 Stripe 余额，商户需要另行安排退款。此时应先核对原 Refund 的最终状态，再决定是否通过其他方式处理，避免一笔售后退款被重复支付。替代方式需要保留金额、币种、客户确认、经办人和凭证，并关联到原订单。

## 争议通知和证据期限

Stripe 当前文档指出，Afterpay 交易可在购买后 120 个日历日内被顾客提出争议。争议打开后，Stripe 会立即暂扣争议金额。商户有 14 个日历日提交证据；Afterpay 会在争议创建后最多 30 个日历日内作出最终决定。争议只能提出一次，部分争议不受支持。

争议通知可以从电子邮件、Stripe Dashboard 和 charge.dispute.created Webhook 到达。争议原因可在 Dashboard 或 Dispute 对象的 reason 字段中查看，证据截止时间可从 Dashboard 或 Dispute 对象的 evidence_details.due_by 获取。收到通知后应立即创建内部任务，不要等到接近截止日期才分配负责人。

证据材料要回应争议原因，并能证明订单已履约。Stripe 文档列出的示例包括物流跟踪号、发货时间、退货确认、数字商品购买记录（例如相关 IP 或邮件收据），以及服务或实物交付记录。收集时只提供与该争议相关且必要的材料，避免提交无关个人数据。

推荐的工作流：

1. 校验 Webhook 签名并读取 charge.dispute.created 事件。
2. 以 Dispute ID 检查是否已经创建过任务，防止事件重试造成重复工单。
3. 从 Dispute 对象保存原因、金额和截止时间，关联 Stripe PaymentIntent、Charge 和内部订单。
4. 通知客服、履约、仓储或服务团队收集对应证据。
5. 由负责人核对材料准确性后，在 Stripe Dashboard 或支持的 API 流程中提交。
6. 记录证据提交时间和最终决定，之后再完成订单财务核对。

Stripe 文档说明，顾客必须登录 Afterpay 账户完成支付授权，这有助于降低欺诈或未授权交易的风险；但它不代表商户可以忽略履约、争议处理或响应 Afterpay 的发货暂停请求。若 Stripe 代表 Afterpay 要求暂停发货，应及时核对请求并按流程处理。

## 退款和争议的 Webhook 对账

Webhook 接收端应先验签，然后持久化事件 ID、对象 ID、事件类型和处理状态。相同事件可能被重复投递，订单状态更新应幂等。若后续系统暂时不可用，可以在保存事件后重试业务动作，避免直接丢弃通知。

可以采用这样的映射：

| 事件/对象变化 | 订单系统动作 |
| --- | --- |
| 支付成功 | 标记付款已确认，启动履约 |
| refund.updated | 更新 Refund 当前状态；只有成功状态才累计已退金额 |
| refund.failed | 将退款标记为失败，通知财务安排替代处理 |
| charge.dispute.created | 创建争议工单，设置 14 天期限和内部更早的提醒 |
| 争议最终更新 | 记录结果并核对 Stripe 余额中的暂扣或返还 |

消费者付款、退款和争议的资金影响可能跨越多个结算周期。报表应同时保留原始付款、退款对象、争议金额、Stripe 余额变化及订单履约记录，而不是只保留一笔订单的最终状态。这样当客服询问、财务对账或争议申诉时，团队可以从订单快速还原完整事件链。

## 上线前检查清单

- [ ] Dashboard 显示当前账户可启用 Afterpay。
- [ ] 业务类别、顾客国家、币种和金额范围符合资格。
- [ ] 选用的 Stripe 产品和 API 在 Afterpay 支持范围内。
- [ ] 动态方式或服务器端规则能避免向不符合条件的顾客展示支付方式。
- [ ] 只有服务端确认付款成功后才触发履约。
- [ ] Refund 对象的异步结果会更新订单，失败会进入人工队列。
- [ ] 退款失败后的替代退款可以关联回原订单并留存凭证。
- [ ] charge.dispute.created 会建任务并读取 evidence_details.due_by。
- [ ] 争议材料收集、审核和提交有责任人，并设置早于官方期限的内部截止时间。
- [ ] Webhook 验签、去重、重试和财务对账已经过测试。

## 总结

Afterpay/Clearpay 能让符合条件的消费者分期付款，但商户仍要处理资格判断、订单确认、异步退款和争议证据。接入前核对账户国家、顾客地区、币种、金额和产品支持；收款后依赖 Stripe 对象状态确认付款；退款时等待最终结果；争议通知到达后尽早收集证据，并在官方期限内提交。

Stripe 的支付方式支持矩阵和时间限制可能调整，正式配置时请以当前账户 Dashboard 和官方文档为准：

- [Stripe Afterpay/Clearpay 支付文档](https://docs.stripe.com/payments/afterpay-clearpay)
- [Stripe Checkout 付款接入](https://docs.stripe.com/payments/checkout)
- [Stripe Refund API](https://docs.stripe.com/api/refunds)
- [Stripe Disputes API](https://docs.stripe.com/api/disputes)
