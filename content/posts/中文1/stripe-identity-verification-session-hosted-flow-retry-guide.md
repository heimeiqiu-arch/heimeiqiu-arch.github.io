---
title: "Stripe Identity VerificationSession 托管验证：创建、重试与服务端确认"
date: 2026-11-15
description: "Stripe Identity VerificationSession 托管流程指南：说明服务端创建验证会话、向用户安全提供 URL、处理 requires_input 重试，并通过 Webhook 确认最终状态。"
slug: stripe-identity-verification-session-hosted-flow-retry-guide
tags:
  - Stripe
  - Stripe Identity
  - VerificationSession
  - 身份验证
  - Webhook
keywords:
  - Stripe Identity VerificationSession
  - Stripe 托管身份验证
  - VerificationSession requires_input
  - Stripe Identity webhook
  - Stripe 身份验证结果确认
---

# Stripe Identity VerificationSession 托管验证：创建、重试与服务端确认

如果网站需要用户提交身份证件或完成自拍验证，Stripe Identity 可以通过 VerificationSession 管理验证流程。托管式流程让用户在 Stripe 提供的页面完成所需步骤，商户后端负责创建会话、把合适的链接交给经过授权的用户，并在之后根据会话状态处理业务。实现看似只要生成一个 URL，但会话生命周期、客户重试、安全访问和最终结果确认都需要明确设计。

常见错误是把“创建会话成功”当成“身份验证已完成”，或者用户完成页面后立刻根据浏览器返回结果开通高权限。VerificationSession 具有状态流转，用户可能退出、提交资料不完整、需要补交信息，或者会话仍在处理中。本文从服务端创建、用户访问、重试和 Webhook 更新说明托管流程，并介绍如何保护验证数据。

## 创建会话时先确定业务用途

VerificationSession 应由服务端创建，并在创建时明确需要的验证类型、选项和与内部用户的关联。不要让前端直接提交任意参数创建高风险验证会话，也不要让用户在 URL 中自行指定需要验证的其他账户 ID。后端应先认证用户、检查该用户是否需要验证、创建内部验证任务，再把 Stripe Session ID 与内部用户、业务原因和创建时间保存下来。

同一用户可能重复点击“开始验证”，因此需要避免无控制地创建大量会话。可以检查是否已有尚未完成且仍可继续的会话，再按 Stripe 当前支持的重试规则复用或创建新会话。每次创建都保存用途、使用环境、Stripe Account 上下文和 session ID，方便后续 webhook 回写正确的本地任务。

验证类型与采集选项要对应实际业务要求。不要为了提高通过率而请求无关的个人数据，也不要把 Identity 当作完整账户安全或反洗钱判断的唯一依据。产品说明和隐私页面应告知用户需要提交的资料、处理目的、验证由谁执行，以及出现问题后如何重试或联系支持。

## 把托管 URL 安全地交给用户

服务端创建会话后，可按当前 VerificationSession 对象提供的托管链接将用户引导到验证页面。只把当前用户、当前会话对应的 URL 返回给浏览器；后端先验证该 session 属于当前账户，不允许仅依赖客户端传来的 Stripe session ID 读取或替换其他用户的验证链接。

托管链接和 client_secret 都应谨慎处理。只通过 TLS 传输，避免记录在公共日志、第三方分析事件、公开工单或跨用户缓存中。页面使用短期登录态或受限的单次操作上下文，避免用户退出后另一个人还能在共享设备上打开验证链接。不要把链接放在公开可索引的页面或群发邮件正文中；如果需要邮件发送，要考虑收件地址验证、链接转发以及会话过期后的处理方式。

测试和正式环境必须隔离。测试会话只能在测试环境流程使用，正式验证数据不得出现在开发日志、截图或演示环境。部署时确认 Stripe key、VerificationSession 对象和 webhook endpoint 使用同一账户及模式。

## 状态流转和补充资料重试

验证会话可能处于需要输入、处理中、成功完成、失败或取消等状态，具体枚举和适用条件要以当前 API 文档为准。对于需要用户补充或重新提交资料的情况，Stripe 文档说明在 requires_input 状态下可以检索有效的 client_secret 或 URL，以允许用户再次提交。重试前先从服务端检索最新会话状态，确认它仍允许用户操作，不要把旧 URL 永久保存在前端或让用户反复访问已失效的会话。

用户返回商户网站时，前端只应展示“已提交，正在确认”或“需要补充资料”等体验提示。成功回跳或页面关闭不代表验证结果已最终处理；用户可能在第三方页面提交后网络中断，后台仍在处理。后端应根据 Webhook 和从 Stripe API 读取的当前 Session 状态更新本地任务。

对 requires_input 这种状态，要区分验证失败、资料不清晰、用户主动退出和系统处理问题。根据实际 last_error 或 Stripe 返回的字段展示可操作提示，避免把敏感的内部风险细节直接暴露给用户。允许重试时，记录原 Session 与新会话的关系，确保最终采用哪次结果有明确规则。

## 通过 Webhook 更新应用状态

为 Identity 流程订阅业务需要的验证事件，并在后端验证 Stripe Webhook 签名。事件处理器应从事件中识别 VerificationSession，再核对它与本地验证任务的映射，确保账户上下文、模式、用户和用途都匹配。相同事件可能重投，因此按 Stripe event ID 做幂等；事件到达顺序也不应作为唯一状态依据。

典型业务处理流程是：Webhook 到达后先将事件 ID 持久化或写入队列；随后检索当前 VerificationSession，确认状态与验证结果；再更新内部任务并发布下一步业务动作。若审核通过后要开放功能、批准提现或允许订阅某项服务，应根据自己的权限规则处理，且将状态变更写入审计日志。不要把前端 JavaScript 自报的“verified”或 URL 查询参数当作授权依据。

Webhook 不可达或处理失败时，建立可重试任务和告警。对长期等待的验证会话，可使用后台任务检查仍处于处理中或需要用户操作的状态，但要限制查询频率。内部状态至少区分待用户操作、处理中、已验证、需要补充、已取消和人工复核，不要压缩成简单的 true/false，否则客服无法判断下一步。

## 隐私、保留和人工复核

身份验证数据比普通订单数据敏感。应用尽量只保存会话 ID、状态、必要的结果引用和业务处理记录，而不是复制或长期存储身份证图片、完整证件号码与自拍图像。日志和客服工具应屏蔽敏感内容，按角色限制访问，并设定保留与删除周期。若有业务或监管要求需要留存资料，应确认 Stripe 提供的数据、权限和保留控制符合自身流程。

自动验证可能需要人工复核。设计支持流程时，客服人员应看到可以采取的动作和状态原因摘要，而不是直接访问所有证件材料。用户请求删除或撤回授权时，明确如何处理 Stripe 对象、本地映射和审计记录；按照适用政策和 Stripe 当前功能完成删除或 redact，不要只清空页面缓存。

验证结果应限于其被收集的目的使用。身份验证通过并不代表用户在所有业务场景中都自动具有某项权限；涉及资金、账户变更或敏感操作时，还应使用适当的登录认证、风控规则和人工审批。

## 上线测试清单

1. 测试服务端创建会话后，只有对应用户能获取托管 URL。
2. 测试用户完成验证、取消、退出、提交不完整和需要重试的路径。
3. 用 requires_input 状态核实服务端如何重新取回有效 URL 或 client_secret。
4. 测试 Webhook 签名错误、重复投递、延迟到达和事件处理器失败。
5. 验证浏览器回跳与真实 Session 状态不一致时，订单仍以服务端数据为准。
6. 检查测试和正式模式使用正确的账户、密钥和 webhook endpoint。
7. 搜索日志、分析平台和工单模板，确认没有身份证件资料、client_secret 或公开验证 URL。
8. 确认状态超时、人工复核、用户重试和删除请求都有处理人和审计记录。

## 总结

Stripe Identity 托管流程由服务端创建 VerificationSession、受控地向用户提供链接、根据状态允许重试，并通过验证过的 Webhook 确认结果。创建成功、用户回跳或前端提示都不是最终验证结论。将会话和内部用户任务明确关联，保护托管 URL 与敏感数据，保持可审计的状态机，并为失败、超时和人工复核准备恢复流程。

请查看 Stripe 的[Identity 验证文档](https://docs.stripe.com/identity)、[创建 VerificationSession API](https://docs.stripe.com/api/identity/verification_sessions/create)、[读取 VerificationSession API](https://docs.stripe.com/api/identity/verification_sessions/retrieve)和[Identity Webhook 事件](https://docs.stripe.com/identity/verification-sessions#webhooks)。
