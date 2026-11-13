---
title: "Stripe Customer Balance 如何抵扣发票？客户余额与交易记录指南"
date: 2026-11-13T13:28:00+08:00
slug: stripe-customer-balance-invoice-credit-transactions-guide
description: "Stripe Customer Balance 是银行卡退款吗？本文解释客户信用余额如何抵扣后续 Invoice、正负金额记录、余额交易对账、退款区别与常见故障处理。"
tags: ["Stripe", "Customer Balance", "Invoice", "账务对账"]
categories: ["支付指南"]
draft: false
---

Stripe Customer Balance 是与顾客账户关联的一种账务余额，可在符合条件时应用于 Invoice。商户可能用它记录顾客多付金额、服务补偿、发票抵扣或其他客户账务调整。但 Customer Balance 不等同于银行账户余额，也不自动表示顾客已经从 Stripe 收到退款。若客服把账户贷方余额称为“银行卡退款”，顾客可能一直等不到资金；若财务只看余额字段而不检查交易记录，发票抵扣也可能无法追溯。

本文说明 Customer Balance 的基本用途、余额交易的正负方向、如何应用到后续 Invoice、和 Credit Note 或 Refund 的区别、记录查询与分页、以及如何安全地对账和测试。它适用于 Stripe Billing 和 Customer 对象相关的一般账务流程。具体余额作用范围、币种限制与应用顺序请以当前 Stripe API 和商户自身账务政策为准。

## Customer Balance 是什么

Customer Balance 是 Stripe Customer 对象相关的账务余额记录，可影响后续发票金额。它不是顾客可以像银行账户一样随时提现的存款，也不代表资金已转入顾客银行卡。实际余额可能作为发票的贷项或借项参与账务计算，商户需要结合 Invoice 的 starting_balance、ending_balance、amount_due、amount_paid 和相关 Customer Balance Transaction 理解。

客户余额通常由一条或多条交易构成。每次调整都会产生 Customer Balance Transaction，记录金额、币种、客户、交易类型、描述和余额变化。与覆盖单一 balance 字段相比，交易流水更适合解释为什么顾客有余额、余额何时应用以及调整来源。商户应把这些流水与订单或客服案例关联。

对客服而言，“账户有余额”并不等于“顾客可以现在提现”。商户应向顾客说明余额会如何用于未来 Invoice，是否可申请现金退款取决于业务政策、支付方式和适用法律。需要退款时，另外查询原支付和 Refund 对象，不能只减少 Customer Balance 来声称已经向银行卡退款。

## 正负金额和余额方向

创建客户余额交易时，金额的正负会影响 Customer 的账户余额方向。Stripe API 的余额交易记录包括 amount 和 ending_balance 等信息，开发者应按照当前 API 对 Customer credit balance 的符号定义进行理解，并在测试环境验证一次贷项和借项的实际发票效果。不要把余额交易的数字符号与 Stripe 账户资金流的正负规则混为一谈。

一种简单做法是给财务系统提供“顾客获得贷项”和“顾客被扣减贷项”的业务按钮，由服务端将业务含义转换为正确的 Stripe 金额符号。不要让客服在后台手工输入一个带正负号的数值，也不要仅凭界面上“balance”旁显示正数就推断顾客欠款还是有余额。应查看对应 Customer Balance Transaction 和下一张 Invoice 的实际结果。

金额需使用正确币种和最小货币单位。Stripe 的 API 通常以整数最小单位处理金额，币种小数位规则可能不同。记录交易时同时保存 ISO 货币代码、业务金额、Stripe amount 和换算规则；不同币种的余额不应在未确认 Stripe 支持行为时直接合并或互相抵消。

## Customer Balance 与 Credit Note 的区别

Credit Note 是针对特定发票的贷项文件，Customer Balance 则是与客户账户相关的余额交易。两者可以有关联，例如开具 Credit Note 后产生客户余额，但并不是同一个对象。Credit Note 主要解释原发票的金额调整，Balance Transaction 记录客户账面余额变化；仅看到其一，不一定说明另一项资金或账务操作已经完成。

如果顾客对某张发票退货或要求减价，应先确定需要更正原发票、减少未付款金额、退回银行卡，还是留下后续抵扣。针对已经收款的交易，可能需要同时处理 Credit Note 和 Refund，或根据策略把金额记入 Customer Balance。每一步的对象 ID 和金额都要关联起来。

不要为了减少当前 Invoice 而随意创建通用客户余额交易，尤其是这项调整应属于某张已开票交易时。这样会让发票与原交易的关联变弱，税务和对账也更困难。按照真实业务原因选择适当对象，保留顾客沟通和审批记录。

## 余额如何用于 Invoice

Customer Balance 可以在符合 Stripe 账单流程时影响后续 Invoice。最终 Invoice 的 starting_balance 和 ending_balance 反映发票处理前后客户余额信息，Invoice 的 amount_due 和 amount_paid 则反映这张发票当前需要支付或已收取的金额。即使金额部分由余额抵扣，商户仍需读取 Invoice 的最终状态，不能假设余额交易创建成功就意味着 Invoice 已 paid。

如果账单使用自动扣款，余额可能先影响发票应付金额，再由付款方式处理剩余款项；若余额足以覆盖金额，Invoice 也可能以余额支付完成。实际行为要通过 Dashboard 和 API 对象核实，尤其是有折扣、税费、部分付款或客户余额交易并发更新时。

对于 send_invoice，顾客收到的 Invoice 应显示余额对发票金额的实际影响。检查 hosted invoice page 和 PDF，确认顾客看到的是抵扣后应付金额，而非原始总价。若客户在发票最终化后增加了余额，应确认该余额会应用到哪张 Invoice，而不是假设已经 finalized 的账单会自动重新计算。

## 如何查询余额交易流水

通过 Dashboard 查看 Customer 的余额和账务记录，或使用 Stripe API 按 Customer ID 查询 balance transactions。列表端点通常支持分页，记录较多时要使用 starting_after 或 ending_before 持续读取，不能只看 API 返回的第一页。每条交易都应核对创建时间、amount、currency、type、description、invoice、credit_note 和 metadata 等字段。

为内部订单或补偿案例添加可搜索的描述和 metadata，例如订单号、服务工单号或审批编号，但避免在 metadata 里写入完整银行卡资料、敏感个人信息或无需长期保留的数据。大规模对账时保存拉取时间和分页游标，避免增量同步时漏掉旧记录。

Customer Balance Transaction 的多数财务字段具有不可变性，通常不能像普通备注一样随意更改金额。若发现错误，应通过新的反向调整或 Stripe 支持的账务流程更正，并保留原始交易。只修改 description 或 metadata 不会改变实际余额。

## 退款、现金余额和客户账面余额的区分

Stripe 还存在其他“余额”概念，例如商户 Stripe 账户的可用资金、Customer Cash Balance 和 Customer Credit Balance。它们代表不同的主体和金融动作。商户账户可用余额反映 Stripe 账户内资金状态；顾客现金余额可能用于特定银行转账付款方式；客户信用余额则用于账单抵扣等客户账务。相似名称不能互换。

Refund 是对已成功收款的一笔付款进行退还，最终要检查 Refund 对象及其状态；Customer Balance 则可被应用于发票。Credit Note 会说明发票金额调整；Customer Cash Balance 则可能代表顾客通过某种方式存入并用于支付的资金。商户应根据顾客的问题查找准确对象。

发生退款咨询时，先识别原 Charge 或 PaymentIntent，再查询 Refund。如果只有 Customer Balance Transaction，清楚告诉顾客款项目前是作为账单抵扣记录，而不是声称银行卡已经收到退款。若需要变更处理方式，按政策执行单独退款或余额调整并做好资金核对。

## 余额币种与汇率问题

Customer Balance Transaction 带有币种，发票也有自己的币种。跨币种客户可能产生多个币种的账单，不能未经验证就将一种币种的余额当作另一种币种的付款。商户应测试实际账户允许的组合，并保存原币金额和账务汇率信息。

若顾客支付货币与商户结算货币不同，Stripe Balance Transaction、PaymentIntent 和 Invoice 可能分别展示不同币种或转换信息。Customer Credit Balance 不应与商户 Stripe payout balance 混算。每月对账时按主体和币种分组，确认每一笔余额调整都对应正确客户及发票。

币种小数位和舍入可能造成几分差异。若 Stripe 将舍入差额记入 Customer Balance，应让财务系统能够识别这类调整，并明确差额处理规则。不要通过人工创建余额交易反复修正几分钱而没有审计说明。

## Webhook 和应用数据库同步

商户需要根据实际集成订阅客户余额交易和 Invoice 相关事件，并通过验证签名后的 Webhook 同步。事件应使用 event.id 去重，关联 Customer ID、Balance Transaction ID、Invoice ID、Credit Note ID 和内部工单。客户余额更新与发票付款事件可能在不同时间发生，不能假设收到一个事件就代表全部会计处理已完成。

存储 Customer balance snapshot 时，将其作为一个当前视图而不是唯一历史依据；真正解释变化的应是完整交易流水。事件失败后，通过 API 回查 Customer 和 Transaction，按时间和对象 ID 修复本地状态。重复 Webhook 不应重复记账或触发两次客服通知。

若商户的 CRM 和 Stripe 都维护客户余额，明确哪个系统是权威来源，禁止两边互相自动覆盖。余额调整应从一个经过授权的操作入口发起，并返回 Stripe 交易 ID；异步同步成功后再更新另外一侧。遇到不一致，冻结自动应用并由财务人员核对。

## 安全、权限和审批

Customer Balance 调整会改变客户之后需要付款的金额，应纳入财务权限管理。普通客服可以查看交易流水或提出调整申请，但高金额贷项、批量调整、跨币种调整和退款应根据公司政策审批。后台应显示操作人、批准人、调整原因、原 Invoice 和外部订单编号。

禁止在公开表单或客户端代码中调用需要 Secret Key 的余额写操作。写接口必须在服务端验证操作者权限、Customer 归属、余额币种、订单状态和重复请求。对自动补偿任务加幂等键或业务唯一标识，避免系统异常时重复增加信用额度。

日志中不记录 Stripe 密钥、完整付款信息和不必要的顾客资料。Customer ID、Balance Transaction ID 和内部订单号通常足以支持技术定位；对财务审计需要的凭证存入具有访问控制的账务系统。

## 常见问题排查

如果顾客有余额但 Invoice 未抵扣，查看余额交易币种、Customer 是否与 Invoice 相同、交易是否已经创建、Invoice 是草稿还是已最终化，以及 Invoice 的 starting_balance、ending_balance 和 amount_due。余额新增的时间可能影响它应用到哪张发票，不能只看客户主页的当前总余额。

如果余额方向和预期相反，检查 amount 符号和 Stripe 当前对象字段，确认是向客户增加贷项还是减少贷项。创建更正交易前先计算现有 ending_balance 和所有相关发票，避免进一步扩大差异。

如果账面有余额但顾客要求退款，查询原始交易来源和合同政策，判断该余额是未用客户贷项、现金余额还是已付款退款。分别检查 Credit Note、Refund 和 Customer Balance Transaction；不要只在自建 CRM 把余额改为零。

如果本地数据库和 Stripe Dashboard 不一致，按 Customer ID 拉取完整分页流水，按时间排序并检查 webhook 漏处理或重复事件。利用 Invoice ID 和 transaction ID 关联，而不是仅按金额和日期猜测。修复时保留差异报告和人工处理记录。

## 测试清单

- 增加客户贷项、减少客户贷项和错误调整后的更正方式。
- 同币种和多币种 Customer Balance Transaction。
- 余额抵扣自动扣款发票及发送账单发票。
- 余额足额、部分抵扣、余额不足和零应付金额。
- Credit Note 关联余额与直接 Customer Balance 调整。
- Webhook 重复、延迟、乱序和分页同步。
- Customer、Invoice 与内部订单映射。
- 报表区分 Customer 余额、现金余额、商户 Stripe 余额和 Refund。
- 高金额调整的权限审批和并发控制。
- 日志中不包含密钥或完整支付凭据。

## 客户余额政策与历史迁移

商户应书面规定哪些情况可以增加客户贷项、哪些情况应直接退款、余额是否可以转给其他客户、是否过期以及顾客如何查询。客服人员不能为了快速结案随意给任何 Customer 写入余额。对于企业客户、转售商和家庭账户，确认法律客户主体和 Stripe Customer ID 一致，不能仅因共享邮箱就把贷项记到另一个账户。

如果从旧系统迁移余额，先导出期初余额、币种、依据凭证、原订单号和更新时间，逐笔形成可解释的交易记录。迁移完成后比较旧系统期末余额、Stripe Customer balance 和首张应用余额的 Invoice。对负数、跨币种或来源不明的历史值，先由财务复核，避免直接批量导入造成不可逆错误。

余额政策变更后，要清楚通知顾客现有余额如何使用、何时失效或是否仍可申请退款，并确认条款符合当地法律。若需要清理过期贷项，使用有审计记录的调整交易，而不是删除历史流水。顾客账务历史应能从调整原因回溯到原订单或客户服务事件。

## 日常监控和异常告警

定期报告未使用客户余额、长时间未抵扣的贷项、最近发生的大额调整、币种不一致和来源缺失的交易。监控不应只看余额总额，还要看交易数量、平均年龄、与退款的关联率和下期发票是否正确应用。遇到异常增长时，暂停相关自动化，按 Customer 和订单抽样核对。

为高风险调整设置阈值和审批，例如单笔超过商户设定金额、同一客户短时间多次调账或一次批量修改大量 Customer。告警应带上安全的 Customer ID、操作人、时间和操作原因，让财务能够快速调查。修复后记录根因，避免同一个重复请求或同步任务持续制造错误余额。

## 人工核对的留痕

任何手动余额调整都应写明原始业务依据、调整金额和币种、相关 Invoice 或 Refund，以及执行和审批人员。后续顾客提出异议时，支持团队可按对象 ID 找到对应流水，而不需要从邮件中猜测。

## 人工核对的留痕

任何手动余额调整都应写明原始业务依据、调整金额和币种、相关 Invoice 或 Refund，以及执行和审批人员。后续顾客提出异议时，支持团队可按对象 ID 找到对应流水，而不需要从邮件中猜测。保留足够的历史版本。

## 总结

Stripe Customer Balance 是与顾客账户关联的账务记录，可影响符合条件的后续发票，但它不等于银行退款，也不等于商户 Stripe 账户的可用资金。准确处理需要查看 Customer Balance Transaction 流水、Invoice 当前状态和相关 Credit Note 或 Refund 对象。

通过明确贷项用途、币种和正负方向，关联订单与审批记录，并在 Webhook 中使用幂等同步，可以避免余额误用和账单错配。顾客询问资金去向时，先确认实际对象，再准确说明是发票抵扣、客户余额还是银行卡退款；财务应分别对账这些不同的账务类型。

官方资料：

- [Stripe：Customer Balance Transaction API](https://docs.stripe.com/api/customer_balance_transactions)
- [Stripe：查询客户余额交易](https://docs.stripe.com/api/customer_balance_transactions/list)
- [Stripe：Invoice 对象和余额字段](https://docs.stripe.com/api/invoices/object)
- [Stripe：支持的币种和金额单位](https://docs.stripe.com/currencies)
