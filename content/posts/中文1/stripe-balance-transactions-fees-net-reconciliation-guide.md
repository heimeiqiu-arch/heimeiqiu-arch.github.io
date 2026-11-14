---
title: "Stripe Balance Transaction 对账指南：手续费、净额与资金状态"
date: 2026-11-14
description: "介绍 Stripe Balance Transaction 的金额、费用、净额、pending 与 available 状态，说明如何将支付、退款、转账和 Payout 纳入财务对账。"
slug: "stripe-balance-transactions-fees-net-reconciliation-guide"
tags: ["Stripe", "Balance Transaction", "财务对账", "支付报表"]
keywords: ["Stripe Balance Transaction", "Stripe 余额交易", "Stripe 手续费对账", "Stripe 净额", "Stripe 财务报告"]
---

Stripe Dashboard 中的付款金额、余额变化和银行出款不是同一个数字。每笔客户付款可能关联 Stripe 处理费用、退款、平台费用或其他余额调整，最终影响 Stripe 账户余额的净额需要结合 Balance Transaction（余额交易）查看。财务团队如果只把 PaymentIntent 金额直接当作入账金额，往往无法解释手续费、退款和跨币种差异。

Balance Transaction 记录一项活动如何影响 Stripe 余额，适合用于交易级对账和资金核查。它通常关联来源对象，并包含金额、费用、净额、币种和资金可用状态等信息。本文说明如何读取这些数据、建立内部账本和核对付款、退款、转账及 Payout。会计科目和收入确认仍应由财务团队按自身政策确定。

## 一、Balance Transaction 与付款对象的区别

PaymentIntent 描述付款流程，Charge 表示扣款记录，Refund 表示退款操作，Transfer 表示 Stripe 账户间的资金移动，Payout 表示资金向外部账户出款。Balance Transaction 则描述相关活动对 Stripe 余额的影响。一个业务订单可能关联多个支付对象和多个余额交易，不能认为一个订单只对应一个余额记录。

例如客户付款的总金额、Stripe 处理费用和净余额增加之间可能存在差异。退款会产生新的资金影响记录，而不是删除原付款。Transfer 和 Transfer reversal 也会分别改变平台或关联账户的余额。对账时应通过 source 等关联信息追到原始对象，同时保留内部订单号和账户上下文。

Balance Transaction 的净影响可根据金额与费用等字段理解，但具体字段语义要核对 Stripe 当前 API 版本和交易类型。不要用一个通用公式替代对每种 reporting category 的检查。某些对象可能涉及外汇费、应用费用、税费或调整，财务报告应保留原始 Stripe 数据。

## 二、金额、费用和净额如何核对

每条余额交易记录币种、金额、费用和净额等信息。金额和费用使用最小货币单位的整数；不同币种不能直接相加。若发生货币转换，应保留交易原币种、Stripe 账户入账币种、汇率或转换信息，并与银行对账周期对应。

在内部账本中至少保存 Balance Transaction ID、source 对象 ID、类型或 reporting category、币种、金额、费用、净额、创建时间、可用时间和账户 ID。支付流程成功时关联 PaymentIntent/Charge；退款时关联 Refund；平台转账时关联 Transfer。不要只在数据库里存一笔付款的“总金额”，因为之后无法解释净到账金额。

费用核对要区分 Stripe 处理费、平台 application fee、外汇费、退款费用和其他调整。不同费用类别的账务处理可能不同；平台不应把所有费用都合并为“手续费”后丢失原始分类。若财务系统需要会计科目映射，建立按 reporting category 的规则版本，并记录何时更新。

## 三、pending 与 available 状态

Balance Transaction 还可以体现资金在 Stripe 余额中的状态，例如 pending 或 available。付款成功并不保证资金立即可提现；待处理资金在满足相应结算条件后才可能转为可用。Payout 只能基于账户可用余额和适用限制创建，银行处理时间又是另一个阶段。

业务后台不要将付款成功直接显示为“已到账”。可以分别展示客户支付已成功、资金仍待结算、Stripe 余额可用、Payout 已发起和银行已入账等状态。客服与财务看到同一组明确状态，可以减少因“订单已付款”被误解为“银行款已到账”的问题。

Connect 平台需要分别核对平台账户与关联账户余额。平台 Transfer 成功只表示账户之间发生了资金移动，不代表关联账户已完成银行出款。读取余额交易时，确认对象属于正确账户上下文，并为每个账户维护独立币种余额和出款记录。

## 四、对账流程如何设计

每日或按财务结算周期，将 Stripe Balance Transactions 与本地订单、支付、退款、Transfer、Payout 和银行流水对比。先按账户与币种分组，再按对象 ID、金额和时间核对。将 pending 和 available 分开，不要把尚未可用的款项当成已出款收入。

对账系统可以识别以下差异：Stripe 有余额交易但内部找不到订单；本地订单标记成功但 Stripe 资金对象仍失败；退款金额不匹配；费用映射缺失；平台 Transfer 与关联账户记录不一致；Payout 金额与银行流水有时间差。差异先进入待检查队列，不要自动覆盖历史数据。

每条修复记录包括原始 Stripe ID、内部订单、差异类型、审核人、修复时间和调整前后值。若需补建订单或修正本地状态，通过审计流程处理，并保留 Stripe 原始对象。对于重复事件导致的重复记账，按交易 ID 和业务幂等键查明根因后再修复。

## 五、Webhook、报告和数据导出

Webhook 适合实时更新支付和退款对象状态，但财务对账仍需要能按时间范围读取余额交易或使用 Stripe 报告。Webhook 可能重复或延迟，余额交易数据也可能在初始事件之后更新。系统应将实时事件处理与周期性财务报告结合起来，而不是只依赖其中一条渠道。

接收 Webhook 时验证签名，可靠保存事件 ID，并用幂等逻辑更新订单。对支付、退款、转账和出款分别建模，保存 Balance Transaction ID 作为资金核对线索。定期导出 Stripe 报表时记录导出时间范围、账户、币种和文件版本，避免同一期间多次导入造成重复行。

报表字段可能随产品版本变化。开发团队要与财务共同确认输出列、时区、账户范围和状态筛选。对部分退款、跨币种和 Connect 交易，抽样核对 Dashboard、API 和内部系统中的对象关联及净额。

## 六、常见错误和测试

常见错误包括把 PaymentIntent 金额当净入账、将不同币种金额直接相加、删除退款原始记录、将 Transfer 当作 Payout、忽略 pending/available 差异、没有关联 application fee、对账仅按客户邮箱和日期匹配，以及把 reporting category 和交易类型混为一谈。

测试成功付款、失败付款、部分退款、全额退款、Stripe 费用、Connect application fee、Transfer reversal、跨币种交易、Payout 失败和余额调整。验证每个 Stripe 对象是否能从内部订单追踪，并确认对账不会因 Webhook 重放而重复记账。准备一份人工核对样例，让财务验证每个金额字段和报告分类。

## 七、SEO 与官方资料

面向商家的 Stripe 对账文章可围绕 Balance Transaction、Stripe 费用、净额计算、退款和 Payout 差异建立专题。标题要说明核对对象，避免承诺报表数字自动等于银行入账。说明币种、账户上下文和状态时间的重要性，并链接官方 API。

官方资料：[Balance Transactions API](https://docs.stripe.com/api/balance_transactions)、[Balance Transaction 对象](https://docs.stripe.com/api/balance_transactions/object)、[Balance 报告](https://docs.stripe.com/reports/balance)、[Stripe 财务报告](https://docs.stripe.com/reports)。

## 总结

Balance Transaction 展示一项活动对 Stripe 余额的资金影响，可帮助财务解释付款金额、处理费用和净额之间的差异。将余额交易与 PaymentIntent、Charge、Refund、Transfer 和 Payout 关联起来，并按币种、账户和资金状态分别核对，才能看清资金实际流向。

通过 Webhook 做状态同步，通过周期性报告做完整对账，差异使用有审计记录的流程修复。尤其要区分 pending 与 available、平台转账与银行出款，并保留原始对象 ID。这样支付系统、Stripe 余额和银行流水才能形成可追踪的财务链路。