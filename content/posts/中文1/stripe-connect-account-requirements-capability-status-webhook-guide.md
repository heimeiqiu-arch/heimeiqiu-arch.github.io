---
title: "Stripe Connect 账户 requirements 与 capability 状态同步实战"
date: 2026-11-14
description: "解释 Connect connected account 的 currently_due、past_due、disabled_reason 与 capability 状态，介绍 account.updated 和 capability.updated 的同步、用户提示及恢复流程。"
slug: "stripe-connect-account-requirements-capability-status-webhook-guide"
tags: ["Stripe Connect", "Connected Account", "Capability", "Webhook", "账户验证"]
keywords: ["Stripe Connect requirements", "Stripe account.updated", "capability.updated", "Stripe currently_due past_due", "Connect capability 状态"]
---

# Stripe Connect 账户 requirements 与 capability 状态同步实战

Stripe Connect 平台需要持续了解 connected account 是否能继续收款、处理付款或使用其他平台功能。账户 onboarding 页面显示“已提交”并不代表所有能力已经启用；Stripe 也可能在后续审核、信息过期或业务变化时要求补充资料。平台如果只在开户当天检查一次账户状态，可能直到付款失败或转账受限时才发现问题。

实现可靠的 Connect 状态管理，应把“资料要求”“账户整体状态”和“每项 capability 的状态”分开建模。Stripe Account 对象中的 `requirements` 会提供当前和未来需要处理的项目、截止时间、验证错误与禁用原因；Account Capability 对象则描述特定能力的申请状态和要求。Stripe 还提供 `account.updated` 与 `capability.updated` 等事件，用于通知账户状态或能力要求变化。[Stripe Account Capability API](https://docs.stripe.com/api/capabilities/update)；[Stripe Events API](https://docs.stripe.com/api/events/types)。

## 账户要求不是单一的“资料完整”布尔值

Connect Account 的 requirements 可以包含多个阶段和状态，例如 `currently_due`、`eventually_due`、`past_due`、`pending_verification`、`errors`、`alternatives`、`current_deadline` 与 `disabled_reason`。应用不应将这些字段简单合并成一个永久的 `verified=true)。某个字段已提交后可能仍在审核中；之前没有立即到期的项目也可能成为后续要求；逾期项目则可能导致账户或能力受到限制。

应根据使用的 Connect 账户类型、当前 API 版本和平台配置读取真实对象结构，不要把某一个文档示例中的字段列表当作所有账户都固定不变的业务规则。账户代表个人还是企业、所在国家、拟启用的业务能力，以及 Stripe 对该账户的审核，都会影响需要收集的资料和状态变化。用户体验应使用可理解的提示，例如“需要补充信息”或“资料正在审核”，而不是向用户展示未经解释的内部枚举和风险原因。

## Capability 与账户整体状态分别判断

Capability 表示账户获得某一类 Stripe 功能的资格或申请状态。常见例子包括 `card_payments` 和 `transfers`，具体能力取决于 Connect 用例和账户配置。Capability 对象包含自身的 `status`、`requested` 和可能存在的 requirements。请求 capability 后，它可能需要一段时间审核；即使请求成功，状态也不一定立刻变成 active。Stripe 的 Capability API 文档说明，设置 `requested=true` 后，如有激活要求，响应会包含相应 requirements；移除部分已申请能力也可能受能力是否永久的规则影响。[更新 Account Capability](https://docs.stripe.com/api/capabilities/update)。

业务授权应直接检查执行操作所需的能力，而不是只检查账户 overall 状态或“已完成 onboarding”。例如平台发起某类收费流程前，检查对应的收款能力是否 active；创建转账前，检查该账户是否具备转账能力以及业务所需条件。即使 API 当前可发起请求，也应处理 Stripe 返回能力不可用或要求待补充的错误，避免将前端展示状态作为唯一授权依据。

## 初始 onboarding 与后续状态更新

创建 connected account 并收集资料之后，平台通常会通过 Stripe 提供的 onboarding 流程引导用户提交信息。用户返回平台页面时，可以重新从服务端检索 Account 对象，为界面展示一次最新快照。但“浏览器跳回成功页面”不是审核完成证明；异步验证和后续要求需要通过 webhook 与服务端检索持续同步。

服务端至少需要保存 Stripe account ID、平台内部用户或商户 ID、账户创建时间、账户类型、关键 capability 状态快照、最后同步时间和需要采取的业务动作。不要为了减少 API 调用而把旧状态长期缓存成不可更新的结论。保存最小必要的状态即可，不要在应用数据库复制不必要的身份证件或敏感审核文件。

为账户事件建立 webhook endpoint，验证签名后将事件写入队列或事件表。接收端快速响应，后台 worker 处理 `account.updated`、`capability.updated` 等相关事件。事件应按 event ID 幂等去重，因为 Stripe 可能重试投递。也要处理延迟与乱序：某个旧事件在新状态之后到达时，不能让本地状态倒退。

## Webhook 事件与 Account API 快照配合

`account.updated` 表示账户信息发生变化，`capability.updated` 表示 capability 的状态或要求发生变化。事件对象有助于触发同步，但平台对高影响操作应根据 Stripe 当前对象重新检索确认。对事件到达时间和本地同步结果做好审计，并在更新数据库时比较对象版本或同步时间，避免两个 worker 同时处理旧、新状态导致覆盖。

不同事件类型通知的资源范围不同。不要假定收到一个 `capability.updated` 就可以推断账户所有 capability 都变化，也不要假设 `account.updated` payload 已包含业务需要的每一项关联信息。通过事件中对象 ID 找到本地账户，再按实际需要检索 Account 或 Capability，并校验对象属于当前平台及正确的测试/正式模式。

Connected account 的 webhook 也要区分账户上下文。平台账户自身事件与 connected account 事件可能涉及不同的对象和处理规则。保存事件关联的 connected account ID（如果事件提供），然后校验它与本地绑定一致，避免把甲商户的状态写入乙商户记录。

## 为不同状态设计用户提示和业务动作

对于 `currently_due`，引导账户负责人继续提交当前需要的信息，并提供重新打开 Stripe onboarding 流程的路径。对于 `pending_verification`，显示审核中，并避免在用户反复刷新时为同一账户创建多个重复 onboarding 入口。对于 `past_due` 或 `disabled_reason`，解释账户可能受到的具体功能影响，并让用户采取 Stripe 要求的行动；不要把所有账户一律展示成“支付失败”。

当某个 capability 尚未 active 时，应仅限制依赖该能力的功能。例如收款能力不可用，不一定意味着平台内所有功能都要关闭；转账能力受限，也不代表普通账户资料页面无法访问。具体限制与 Stripe 当前账户状态和平台自身风险策略一致。前端提示可以帮助用户理解下一步，最终的操作权限仍要由服务端在每次资金相关操作前重新判断。

若 Stripe 返回 `alternatives`，应按照当前对象和 onboarding 流程提供的选择处理，而不是要求用户机械填入所有可能的字段。若 requirements 中有错误，展示经产品审核的说明和修复路径，不要原样暴露可能包含内部验证细节或对用户难以理解的错误内容。

## 运营监控与人工支持

建立按状态变化的运营视图：新增待处理要求数、逾期账户数、待审核时长、关键 capability inactive 数，以及 webhook 投递失败和状态同步延迟。按国家、账户类型或 capability 分组可以帮助发现 onboarding 文案或业务流程问题。监控设计应遵循数据最小化原则，只保存排障和业务操作需要的信息。

支持人员处理账户问题时应基于 Stripe Dashboard 和最新 Account 快照核对，而不是依赖用户截图或旧缓存。记录客服查看的时间、账户 ID 和采取的操作；如需联系 Stripe 支持，准备相关事件 ID、时间和账户标识，不要在普通工单中分享无关的完整个人资料。平台内部也要规定谁有权暂停、恢复或批准高风险资金操作。

## 常见故障排查

**Onboarding 显示已完成，但能力仍不是 active：**检查具体 capability 的 status 与 requirements，并确认是否仍处于审核或需要补充资料。不要只根据 onboarding 页面跳转结果开通全部业务。

**账户状态在 Stripe Dashboard 已更新，本地仍旧：**检查 endpoint 是否订阅相关事件、签名验证是否成功、事件是否进入队列、worker 是否处理失败以及本地账户绑定是否正确。可以服务端检索当前 Account 快照进行修复性同步，并记录重新同步来源。

**本地要求清单重复或已补交仍显示待处理：**核对是否将旧 webhook 事件覆盖新快照，检查处理是否幂等，以及界面是否在账户资料提交后主动刷新。对存在乱序的事件，优先根据对象当前状态重建本地快照。

**转账 API 失败但账户标记为可用：**确认业务判断的是 `transfers` 对应 capability 和实际操作需要，而不是只检查 charges_enabled、payouts_enabled 或某个历史布尔值。不同能力与操作应分别映射。

## 上线检查清单

- 本地账户记录以 Stripe account ID 与内部商户 ID 建立不可混淆的映射。
- 分别保存 Account requirements 和每一项关键 Capability 的状态。
- 前端回跳结果不被当作审核通过的最终依据。
- 订阅 `account.updated` 和 `capability.updated` 等适用事件，并验证 webhook 签名。
- 事件按 ID 幂等处理，并能防止延迟事件覆盖更新状态。
- 关键资金操作在服务端检查所需 capability 并处理 Stripe API 错误。
- 用户提示按待提交、审核中、逾期或能力受限提供不同操作路径。
- 测试模式、正式模式及 connected account 上下文彼此隔离。

## 总结

Connect 账户的资料要求、账户状态和各项 capability 需要分开管理。平台应以 Stripe Account 和 Capability 的当前数据为依据，通过可靠 webhook 持续同步；对收款、转账等关键操作，在服务端检查对应能力，而不是依赖一次 onboarding 完成标记。把异常恢复、状态更新、客户提示与运营监控都纳入设计，能减少“页面看起来已完成、实际能力仍不可用”的问题。

Connect 账户类型、要求字段和 capability 可用性会受平台配置、国家/地区及 Stripe 当前规则影响。请以账户实际 API 响应和 Stripe 官方文档为准。
