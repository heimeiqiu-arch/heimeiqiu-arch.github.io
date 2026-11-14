---
title: "Stripe Customer Cash Balance 银行转账对账：资金到账与发票核销"
date: 2026-11-14
description: "介绍 Stripe Customer Cash Balance 银行转账资金如何进入客户余额、自动或手动匹配发票，说明 funds_available 事件、部分入账、余额明细和对账设计。"
slug: "stripe-customer-cash-balance-bank-transfer-reconciliation-guide"
tags: ["Stripe", "Customer Cash Balance", "银行转账", "Invoice"]
keywords: ["Stripe Customer Cash Balance", "Stripe 银行转账对账", "cash_balance.funds_available", "customer_balance_transaction", "Invoice 自动核销"]
---

# Stripe Customer Cash Balance 银行转账对账：资金到账与发票核销

面向企业客户或大额订单时，银行转账可能比银行卡更适合付款。Stripe Customer Cash Balance 可以为 Customer 维护按币种区分的客户现金余额，并在资金到账后根据设置自动或手动与未结发票核销。接入时要区分客户的现金资金余额与一般客户信用余额：前者涉及银行转账资金入账和余额可用情况；后者通常是商家授予的账户 credit，用于抵扣未来发票。两者名称相似、对象和资金来源不同，不应在账务中混为一谈。

Stripe 的 Cash Balance 对象包含客户当前可用余额和余额设置；资金有变动时可以通过相关 webhook 获知，例如 cash_balance.funds_available 表示客户现金余额出现可用资金，customer_cash_balance_transaction.created 则记录一笔客户现金余额交易。余额与发票抵扣情况还应结合 Invoice 的 amount_due、amount_paid、amount_remaining、paid 和 ending_balance 等字段核对。[Cash Balance API 对象](https://docs.stripe.com/api/cash_balance/object)；[Stripe 事件类型](https://docs.stripe.com/api/events/types)；[Customer Cash Balance Transactions](https://docs.stripe.com/api/customer_balance_transactions/list)。

## Customer 现金余额和信用余额的区别

Customer Cash Balance 与 Customer balance/credit balance 的业务含义不同。现金余额体现客户经银行转账等方式转入的资金，可能按币种维护，并受 reconciliation_mode 设置影响；客户信用余额则可以是商家通过调整或信用交易授予客户的账单抵扣。内部数据模型应把资金来源、余额类型、币种、Stripe 对象和对应发票分别记录，不能把它们都简化为一个“账户余额”。

客户现金余额中的资金也不是直接打到商家银行账户的“客户钱包”通用概念。资金何时可用、是否自动分配到发票、转账说明和 reconciliation 方式，都依赖 Stripe 支持的地区、支付方式和账户配置。对外文案应清楚说明客户使用的是转账支付方式和未匹配资金处理规则，不能夸大为随时可提现的储值账户。

在应用账务中建议分别建模 Stripe Customer、现金余额对象、余额交易、Invoice 和本地付款分配记录。保存 Stripe ID、金额和币种、事件发生时间、订单或账单号以及本地 reconciliation 状态。任何显示给客户的“已到账”“已核销”都应来自服务端读取的 Stripe 对象和内部核对结果。

## 自动和手动 reconciliation

Cash Balance settings 中的 reconciliation_mode 可以是 automatic 或 manual。自动模式适合希望 Stripe 按规则处理客户转入资金并尝试将其用于客户相关发票的业务。手动模式则让商家在收到余额资金后，由自己的流程确定何时以及如何应用。具体匹配规则、可用发票范围和支付方式支持受 Stripe 产品和账户配置影响，上线前要核对当前地区文档与 Dashboard 设置。

自动核销减少了人工步骤，但系统仍需要监听事件并更新内部账务。资金入账通知不等同于某一张特定 Invoice 已付款；客户可能有多张账单、账单币种不同，或者转入金额不足以覆盖整个应付金额。服务端应在收到事件后读取 Customer Cash Balance 和相关 Invoice，确认金额分配后的账单状态，再更新订单。

手动 reconciliation 提供更强的财务审批和分配控制，但需要建立待处理队列。财务人员可根据客户引用、转账金额、币种、账单号和付款人信息核对后执行适当操作。系统应记录谁批准了分配、何时分配、关联哪张发票，以及余额交易 ID。对于无法匹配的资金，应进入未分配款项队列，而不是默认为收入或自动关联到最近的一笔订单。

## 监听资金到账与交易事件

cash_balance.funds_available 可以提示客户现金余额有可用资金；如果账户使用手动 reconciliation，事件也可用于提醒商家有新资金需要处理。customer_cash_balance_transaction.created 可记录新的余额交易。Webhook 必须验证 Stripe 签名，事件 ID 需要去重，并要处理重复、延迟和乱序投递。

Webhook 处理器收到事件时，先检查 livemode、Stripe account context 和 Customer ID，再找到本地客户和未结账单。尽量把事件快速写入队列后返回成功，避免因同步查询过慢导致 Stripe 重复投递。后台 worker 负责拉取最新余额和 Invoice 状态，事务性地更新本地 reconciliation 记录。事件只是同步信号；如果处理逻辑失败，可用重试队列或定时对账重新读取 Stripe 当前状态。

事件可能表示余额有变化，但未必代表新订单对应的 Invoice 已结清。订单发货、开通付费权益或关闭应收账款前，应核实 Invoice paid 状态以及 amount_remaining 是否为零，并按业务允许的支付方式检查对应的付款来源。不要只以“收到了一笔现金余额事件”作为已履约的条件。

## 金额、币种与部分到账

Cash Balance 按货币计量，所有金额单位应遵循 Stripe 对象中的币种和最小单位定义。不要把不同币种直接相加，也不要将整数的最小货币单位误显示为标准单位。客户可能转入的金额与发票总额不同，系统需识别部分资金、超额资金、未分配余额及产生的差额。

发票对象中的 amount_due 可能受到客户余额抵扣等因素影响，实际应收金额不一定等于商品列表的总额。Invoice paid 也可能来自客户账户余额抵扣，而不一定是信用卡成功扣款。财务报表应能区分银行卡收款、客户现金余额应用、商家信用抵扣和 out-of-band 人工标记付款等不同来源，避免把它们统称为“卡支付成功”。

如果账单只部分覆盖，订单系统要明确是否允许部分付款后交付、是否等待剩余金额，以及未付金额如何提醒。对于预付款场景，可以将入账资金作为待分配余额，等客户指定发票或通过合同规则分配。不要在没有本地账务记录的情况下把余额静默用于任意账单。

## 对账与客户服务流程

日常对账应比较 Stripe Cash Balance、余额交易、Invoice 状态和本地银行转账参考。对于手动核销，可以将客户提交的参考号与 Stripe 银行转账信息一起展示，但应将客户输入视为辅助信息，而不是唯一依据。转账金额、到账时间、币种和付款账户可能存在差异，要允许人工核查。

客户咨询“已转账但订单仍未付款”时，支持人员应能查看 Customer ID、资金是否进入 cash balance、当前 reconciliation_mode、余额交易时间、目标 Invoice 状态和最近 webhook 处理结果。如果钱已到账但没有自动应用，检查发票是否属于同一 Customer、币种是否匹配、自动 reconciliation 设置是否适用，以及是否有更早的未结发票按规则先被抵扣。

对于错配或退款，应遵循 Stripe 当前资金处理 API 和企业财务流程。不要通过简单修改本地余额数字来弥补 Stripe 对象差异。系统需要留存退款、撤销、余额交易和原发票之间的关联，以便会计审计能追溯完整资金流。

## 安全与权限

银行转账账号和参考信息需要妥善保护。服务端 API key 和 webhook signing secret 只能存在于服务端安全配置中。客户仅可查看自己账户的余额和发票，客服与财务权限应按职责分级。前端传来的 Customer ID、Invoice ID 和金额都需要服务端验证归属。

在多人协作或 Stripe Connect 架构中，要明确余额属于平台 Customer 还是 connected account 下的客户。API 调用使用的平台账号上下文、Customer 所属账户和 Invoice 签发账户必须保持一致。跨账户 ID 看似可读，不代表对象可以跨账户使用。

## 测试清单

- 在测试模式验证 Customer Cash Balance 与银行转账方式的可用性。
- 覆盖 automatic 和 manual reconciliation 的预期流程。
- 模拟到账金额不足、超过应付金额和多张未结发票。
- 检查 funds_available 与 cash balance transaction 事件的重复和延迟处理。
- 订单只有在服务端确认 Invoice 达到付款完成条件后才履约。
- 确认币种、最小货币单位和账单抵扣计算正确。
- 手工分配余额时保存审批人、发票和交易 ID。
- 验证未匹配资金有待办队列，不会被当作销售收入。
- 检查 Stripe Customer、Invoice 和余额交易属于预期账户和环境。
- 定期比较 Stripe 与本地账本，发现差异后可重新同步。

## 总结

Customer Cash Balance 是 Stripe 对客户现金余额和相关入账资金的管理对象，可与 Invoice 付款和余额对账流程配合。实现时应区分现金余额和商家信用余额，明确自动或手动 reconciliation 策略，使用 webhook 发现变更，再通过服务端读取 Cash Balance、余额交易和 Invoice 当前状态核实是否真正核销。按币种、订单和交易来源保留账务链路，能帮助处理部分到账、未分配款项和客户争议。

本文为技术实现参考。银行转账、现金余额及可用币种因地区与账户配置而异，资金与账务政策应由商家结合 Stripe 当前文档和会计要求确认。
