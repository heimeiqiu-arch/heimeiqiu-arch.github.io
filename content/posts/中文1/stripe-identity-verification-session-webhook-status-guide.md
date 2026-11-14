---
title: "Stripe Identity VerificationSession 集成：状态流转、重试与隐私处理"
date: 2026-11-14
description: "介绍 Stripe Identity VerificationSession 的创建、前端验证、requires_input 重试和 webhook 同步，说明 verified 状态边界、权限控制及个人数据保护。"
slug: "stripe-identity-verification-session-webhook-status-guide"
tags: ["Stripe", "Stripe Identity", "VerificationSession", "Webhook"]
keywords: ["Stripe Identity VerificationSession", "Stripe Identity verified 状态", "verification_session.requires_input", "Stripe 身份验证 webhook", "Stripe Identity 数据隐私"]
---

# Stripe Identity VerificationSession 集成：状态流转、重试与隐私处理

Stripe Identity 可以帮助商家在需要身份核验的流程中创建 VerificationSession，让客户通过托管或嵌入式流程提交所需验证资料。Identity 集成并不只是“把用户跳转到上传证件页”：服务端要为当前业务创建会话、保存它与应用用户和订单的关联，前端引导客户完成流程，再通过 webhook 和服务端检索确定状态。与此同时，身份证件和验证报告属于高度敏感信息，商家需要限制访问并设计数据保留策略。

VerificationSession 常见状态包括 requires_input、processing、verified、canceled 等。客户未完成或提交内容有问题时，状态可能回到需要输入；在 requires_input 状态下，服务端可检索会话并取得当前有效的 client_secret 或 url，让客户重新提交。Stripe 提供 identity.verification_session.created、processing、requires_input、verified、canceled 和 redacted 等事件，用来同步会话生命周期。[VerificationSession 查询 API](https://docs.stripe.com/api/identity/verification_sessions/retrieve)；[Identity 事件类型](https://docs.stripe.com/api/events/types)；[Stripe Identity 指南](https://docs.stripe.com/identity)。

## 创建验证会话并绑定业务对象

创建 VerificationSession 应在服务端进行。用户必须先通过应用身份认证，服务端根据当前登录主体读取自己的用户或企业资料，再创建所需验证类型的 Session，并在 metadata 或自己的数据库中关联本地 user_id、订单号、用途和创建时间。不能让浏览器直接指定任意 Customer、user ID 或验证会话 ID，否则可能把一个人的验证结果错误地应用到另一账户。

会话类型和选项应与实际核验目标匹配。只收集完成业务所需的最少信息，不要为了“多拿一点资料”默认要求所有可用的证件和附加自拍。具体类型、可用国家及核验选项应按 Stripe 当前产品能力和账户配置确认，不能将某种测试环境可用性推断为正式账户一定支持。

服务端创建后，将会话对应的客户端流程信息安全地传递给已认证用户。client_secret 或 url 只应提供给当前验证者，避免写入公开日志、分析事件、长效缓存或 URL 参数。TLS 必须启用，并设置请求授权检查和合理的速率限制，避免第三方反复创建验证会话。

## 前端引导和可恢复流程

前端负责引导客户打开 Stripe Identity 验证界面，并展示等待、完成或需要重新提交的状态。用户可能关闭窗口、网络中断、拒绝摄像头权限或在上传过程中离开，因此前端回调不能作为最终验证结果的唯一依据。客户返回商家页面后，应用应向服务端询问当前验证状态；服务端再读取 Stripe 对象或使用已验证的 webhook 更新本地记录。

当 Session 为 requires_input 时，可以通过服务端检索该会话，获取当前有效的重新提交入口，再让客户继续验证。不要在浏览器中无限复用可能已经失效的 client_secret，也不要每次刷新页面都创建新 Session。一个用户同时存在多个未完成会话时，应用应明确当前哪一个与业务流程关联，并对旧会话进行清理或取消。

如果状态是 processing，应让客户知道系统仍在处理，避免错误显示“验证失败”或允许其通过创建大量会话绕过核验。如果状态为 canceled，通常需要根据业务策略重新开始一条新会话，而不是试图恢复被取消的会话。用户可见消息应简洁，不暴露内部风控判定、匹配算法或未经确认的失败原因。

## Webhook 状态同步

Webhook 是服务端同步 VerificationSession 生命周期的重要途径。接收端首先校验 Stripe 签名，再检查事件所属账户、livemode 和关联的 Session ID。将事件写入可靠队列并快速返回成功，异步 worker 再更新本地验证状态、发送通知或授权后续业务。

事件至少要按 event ID 去重。重复或乱序事件不能把已 verified 的当前状态回退成 processing，也不能让 canceled 会话覆盖另一个新建 Session 的成功结果。对关键授权，可以在 webhook 到达后再次检索 Stripe VerificationSession，核对当前状态和最后的验证报告，再更新订单或账号。

要为 identity.verification_session.redacted 事件建立后续处理逻辑。Redaction 与正常验证成功、取消、失败不同，意味着相关数据处理或删除流程已经发生。应用要按自身保存策略更新记录，并避免仍从旧缓存或日志中暴露已处理的数据。

## verified 不等于业务永久放行

verified 表示该 VerificationSession 达到了 Stripe 所报告的验证结果，但应用是否放行某项服务，仍需结合业务规则、Session 类型、使用目的和账户风险策略判断。不要把“用户历史上曾经 verified”永久当作当前账号没有风险的证明；验证结果可能只适用于特定用途或时间范围。对于重要的账户恢复、资金操作或高风险交易，可以要求与场景匹配的重新核验。

本地数据库最好将状态拆分为会话状态、业务授权状态和审查状态。例如 Session verified，但人工复核仍待完成；Session requires_input，业务仍允许访问普通功能但不允许提款；Session canceled，需要用户重新开始验证。这样能避免把一个布尔字段 verified=true 用于所有业务判断。

Webhook 事件可触发授权更新，但每次敏感操作仍由后端重新检查用户所属关系和当前权限。前端隐藏提款按钮或显示绿色勾选，不构成资金操作的服务端授权。

## 个人数据和访问控制

身份验证可能涉及政府身份证件、自拍、生日、姓名、地址或验证报告。将完整原始信息的访问限制在确有需要的服务和授权人员范围内。不要把身份证件图像下载到自己的存储桶，除非业务、法律和 Stripe 流程明确要求并已完成安全评估。避免把照片、完整姓名或报告内容放进普通应用日志、客服聊天记录和产品分析事件。

只保存业务需要的字段，例如 Stripe VerificationSession ID、当前状态、用途、关联账户、必要的完成时间和审核结论。若客服需要排查，只开放掩码或受控的 Stripe Dashboard 链接，并在访问时记录人员、原因和时间。会话 ID 也不是公开识别码，仍应放在授权保护后的系统内。

定义数据保留和删除流程：保存本地状态的周期、用户删除账户时的处理方式、Stripe 侧数据 redaction 的请求流程、事件队列和备份的清理周期。删除后仍可能需要保留最少的交易或审核记录以满足业务要求，应由法律和隐私负责人确定规则。

## 安全和故障排查

如果客户显示已完成但应用仍未放行，检查 webhook 是否投递失败、服务端是否用正确 Session ID 查找本地账户、是否将测试模式事件误用到正式账户，以及当前 Stripe 对象状态是否与缓存一致。若 Session 一直 processing，不要向客户承诺固定完成时间，按照当前产品说明提供等待或联系支持路径。

如果用户可以看到他人的验证状态，优先检查会话创建时的本地用户绑定、查询接口是否只按客户端提供的 Session ID 返回，以及是否缺少当前账户校验。检查服务端返回的 client_secret 是否被缓存到共享页面或第三方日志中。

配置 API 版本时，确认 webhook endpoint 的版本与服务端 SDK 兼容。Stripe webhook 事件使用 endpoint 所配置的 API 版本结构；升级时应在测试环境比较字段变化并处理旧事件格式。

## 测试清单

- 测试 Session 创建、成功验证、requires_input、processing、canceled 和 redacted。
- 用户关闭窗口或断网后，重新打开流程能获取当前有效会话。
- Webhook 重复、乱序和延迟不会回退本地状态。
- 用户只能访问自己的 Session，不能用更改 ID 查询他人身份结果。
- client_secret 不出现在 URL、日志或公开前端代码中。
- 支持人员只能在授权范围内查看敏感验证结果。
- verified 会按不同业务场景进行授权，而不是全站无条件放行。
- 账户删除和 redacted 事件会触发本地数据清理流程。
- 测试与正式模式的 Session 和 webhook 完全分开。

## 总结

Stripe Identity VerificationSession 需要服务端创建与用户绑定，前端引导验证，并通过签名验证的 webhook 和 API 检索同步结果。requires_input 可支持客户重新提交，processing 和 canceled 需要不同的产品体验，verified 也不应被误解为对所有业务永久放行。将会话状态、业务授权和个人信息保留分开管理，可以让身份核验流程更安全、也更容易恢复和审计。

本文为工程集成参考。Identity 可用性、验证选项和数据处理规则因账户与地区不同，请以 Stripe 当前文档和适用的隐私要求为准。
