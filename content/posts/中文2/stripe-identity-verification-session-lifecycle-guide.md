---
title: "Stripe Identity VerificationSession 接入指南：创建、重试、结果与隐私删除"
date: 2026-11-19
slug: stripe-identity-verification-session-lifecycle-guide
description: "梳理 Stripe Identity VerificationSession 的完整生命周期：验证类型选择、服务端创建、client_secret 安全传递、requires_input 重试、Webhook 处理和 PII 删除。"
keywords:
  - Stripe Identity VerificationSession
  - Stripe Identity 身份验证
  - Stripe VerificationSession 状态
  - Stripe Identity Webhook
  - Stripe client_secret 安全
  - Stripe 身份验证重试
tags:
  - Stripe
  - Stripe Identity
  - 身份验证
  - 数据隐私
---

在线平台需要确认用户身份时，常见需求包括核验政府签发的身份证件、检查身份证号码，或在特定场景中完成自拍比对。Stripe Identity 的 Verification Sessions API 用一个 Session 对象跟踪验证流程，从创建、用户提交材料、验证处理中，到通过、需要补充输入、取消或脱敏删除。把 Session 的状态流转理解清楚，可以避免把“用户已经上传证件”误当成“身份验证已经通过”。

本文介绍 VerificationSession 的服务端创建、前端接续、结果读取、失败重试、Webhook 状态更新和个人信息删除。身份验证会处理高度敏感的个人信息，产品设计不仅要能调用 API，还要考虑账户授权、用户告知、数据最小化和申诉流程。当前可用验证类型、功能资格及数据处理细节应以 Stripe 官方文档和适用法规为准。

## VerificationSession 的职责

VerificationSession 是一次身份验证过程的状态容器。创建时选择要执行的验证类型，用户通过 Stripe 提供的流程提交资料，Stripe 处理后更新 Session 状态并产生 VerificationReport。开发者可以通过对象 ID 查询状态，并在所有所需检查通过后查看 verified_outputs。

文档列举的常见验证类型包括 document 和 id_number。document 类型用于验证政府签发证件的真实性和归属，也可以配合自拍检查；id_number 类型用于核验用户姓名、出生日期和国家身份证号码。不要在未确认自己业务目的、适用地区和资料采集依据前，就默认要求所有用户提交完整身份证件。

Session 解决的是一次核验流程的跟踪，不等于平台自己的账户安全系统或合规判断。业务方仍要决定何时启动核验、谁可以发起、成功后开放哪些功能、失败后是否允许重试，以及如何处理用户申诉。

## 服务端创建 Session 并关联内部用户

通常由服务端创建 VerificationSession。创建请求选择验证类型，可以设置非敏感 metadata 将 Stripe Session 与应用内部用户 ID 关联。Stripe 建议为创建请求使用幂等键，通常以平台内部为这次验证分配的稳定 reference 为基础，避免网络重试或用户重复点击时创建多条重复 Session。

把 Session ID 保存在内部用户验证记录中，后续中断时优先复用该 Session，而不是每次访问都创建新的对象。复用同一 Session 有助于保留验证尝试历史；如果前一次检查失败，Session 可能处于 requires_input，用户可以按当前对象状态继续补充输入或重试。

metadata 不应保存身份证号、生日、地址、证件图片或其他敏感个人信息。它会出现在 Dashboard 和报告中，适合存储内部引用，不适合复制验证表单内容。把 Stripe Session ID 和内部用户 ID 映射保存在权限受控的服务端数据库，避免让客户端能够将一个用户的 Session ID 绑定到另一个账户。

## client_secret 的安全传递

VerificationSession 含有 client_secret，前端需要它来完成该 Session 的验证。推荐的方式是前端向经过身份验证的商家后端请求 client_secret，再由后端只向当前待验证的用户返回对应值。后端必须先验证会话登录状态、用户 ID、VerificationSession 所有权和当前流程权限。

client_secret 是敏感令牌。Stripe 明确建议不要将其写入日志、放入 URL 或暴露给除当前被验证用户之外的对象。包含该令牌的页面必须使用 TLS。前端错误收集、会话回放、分析埋点和第三方脚本也要检查是否会捕获请求响应或页面内容。

如果用户刷新页面或更换设备，不应通过把 client_secret 作为查询参数发送给邮件链接的方式恢复流程。应让用户重新登录，再由服务端查询并返回当前 Session 允许使用的 URL 或 secret。令牌泄漏时，按敏感凭证事件处理并检查受影响 Session 状态。

## 状态不是简单的成功和失败

常见状态包括 processing、verified、requires_input、canceled 等。用户提交资料后，Session 进入 processing，验证流程通常会在几分钟内更新结果；只有所有检查通过，才成为 verified。若有任何检查未通过，Session 会进入 requires_input，并在 last_error 中提供错误代码和原因。

requires_input 代表当前验证未通过或需要额外输入，并不一定意味着用户被永久拒绝。错误可能是证件过期、图像质量不佳、信息缺失或其他验证问题。产品可以将适合用户理解的原因显示出来，并指引其重新提交，但要根据错误类别避免泄露不必要的风控信号。

若用户要再次尝试，先检索现有 VerificationSession，按其状态获取新的 URL 或 client_secret，再提供给前端。不要直接在错误回调中无限创建 Session。重复创建会让用户有多个未完成验证对象，增加审核和隐私删除复杂度，也使内部状态难以判定哪一次才是当前有效流程。

取消 Session 会使它进入 canceled，后续不能继续提交；Stripe 文档说明，在 processing 或 verified 等阶段不能随意取消。取消操作不可逆，因此在用户撤回、账户关闭或验证流程需要终止时，要先确认对象状态并向用户说明后果。

## 使用 Webhook 更新业务状态

VerificationSession 状态变化会产生事件。常见事件包括 identity.verification_session.created、processing、verified、requires_input 和 canceled。若业务要接收脱敏完成通知，需要为 Webhook endpoint 显式订阅 identity.verification_session.redacted；Stripe 文档指出，订阅所有事件的 endpoint 未必会收到 redacted 事件。

Webhook 负责把 Stripe 的验证状态同步到内部系统。收到事件后，验证签名，按事件对象 ID 查找用户验证记录，更新状态并触发后续动作，例如通知用户验证成功或提醒补充资料。不要只依赖前端验证组件回调来开通账户，因为用户可能关闭页面，网络也可能中断。业务应以服务端已验证的 Stripe 状态为依据。

事件可能延迟或重复到达，内部状态更新需要幂等。保存事件 ID、VerificationSession ID、事件类型和处理时间；遇到重复事件时不重复发通知或开通权益。若新旧状态顺序看似冲突，可在必要时重新检索 Session 当前状态，避免用迟到事件覆盖较新的结果。

验证成功之后才读取 verified_outputs，并仅在业务确有必要时保存所需字段。Stripe 文档说明，verified_outputs 可能包含姓名和地址等核验数据。将结果映射到内部账户时，应避免把整份 JSON 长期保存到普通日志或面向客服的宽泛数据库中。

## 失败恢复与客服处理

可以为用户设计一条可理解的恢复路径：用户收到需要补充资料的提示；页面解释问题类别和允许的重新提交方式；后端检索现有 Session；前端获取该 Session 对应的新 URL 或 client_secret；用户提交后，系统等待 Webhook 更新结果。对证件过期等可解释错误，可以给出更新证件的指引；对无法由用户自行解决的错误，提供人工支持入口。

客服后台应显示必要的状态、错误类别、上次尝试时间和是否允许重试，但避免直接显示证件号码、完整出生日期或证件图像。客服确认身份时也应遵循平台自己的权限和隐私政策，不能通过普通邮件要求用户发送完整证件图像到未受保护的渠道。

当验证服务暂时不可用时，产品要明确策略：暂停需要高置信身份的操作、允许不涉及风险的基础浏览，或提供稍后重试。服务错误不应直接转成“用户身份不真实”的判定。记录调用失败、超时、Stripe API 请求 ID 和 Session ID，可帮助工程团队诊断但不泄露用户资料。

## 删除个人信息与会话脱敏

当收到合法的数据删除请求或不再需要保留验证个人信息时，可以按照 Stripe 支持的流程 redaction VerificationSession。脱敏后，个人信息不再通过 API 返回或在 Dashboard 中查看，相关 VerificationReport、事件、请求日志和上传文件也会按 Stripe 的机制处理。脱敏操作之后仍可查询 Session，但不能再更新，且不能下载已删除的文件内容。

脱敏可能需要时间。Stripe 文档说明 redaction 最长可能需要数日完成，并会发送 identity.verification_session.redacted 事件。若 Session 正处于 processing 状态，需要等待处理结束才能执行脱敏；对某些仍待用户操作的状态，脱敏会同时取消后续提交。

平台还要检查自己的数据副本。Stripe 删除不等于自动删除你在内部数据库、日志系统、对象存储、客服附件、备份和分析平台中的资料。建立数据映射，以内部用户 ID 查找所有相关副本，按本地保存政策执行删除或匿名化，并记录处理结果。metadata 中不应存入本来就不该保留的个人信息。

## 生产上线前的安全清单

**流程与权限：** 身份验证只在明确业务需要时触发；创建 Session 时通过后端确认用户登录和权限；使用稳定的幂等键；保存 Session ID 并在用户返回时复用。

**令牌保护：** client_secret 仅返回给当前被验证用户；传输使用 TLS；不放在 URL、前端持久存储、日志、错误追踪或第三方分析中。

**结果处理：** 使用服务端 Webhook 更新业务状态；对事件验签和幂等；只有 verified 才认为所需检查通过；requires_input 展示适当修复提示，不自动永久封禁用户。

**数据治理：** metadata 只放非敏感内部引用；按最小原则读取 verified_outputs；建立内部资料留存和删除映射；处理 Stripe redaction 与本地系统删除流程。

**测试覆盖：** 测试正常通过、证件过期、资料需补充、用户中途关闭、重复创建、重试、Webhook 重投、取消和脱敏等情况；验证测试和生产模式密钥、事件 endpoint 及权限隔离。

## 常见问题

### Session 处于 requires_input，可以直接重新创建吗？

一般先检索并复用现有 Session，再根据 last_error 获取适当重试路径。Stripe 建议复用 Session 以保留尝试历史，并用幂等键避免相同验证被重复创建。

### 前端可以直接保存 client_secret 吗？

只在完成当前验证所需的短期上下文中使用，并避免日志、URL、长期本地存储或第三方脚本访问。后端只应把它返回给经过身份验证且拥有该 Session 的用户。

### 身份验证通过后是否立即开通所有功能？

由业务策略决定。验证通过表示所选检查已完成，不自动决定你是否满足其他账户、法律、风险或产品条件。将身份结果与自己的授权系统分开。

### 用户申请删除资料后，只调用 Stripe redaction 就够了吗？

不够。还要定位并处理商家自己保存的数据副本、日志、客服附件和分析记录，并按适用法律和保留政策进行操作。

## 总结

Stripe Identity VerificationSession 是跟踪用户身份核验的生命周期对象。安全集成应由服务端创建并管理 Session，安全传递 client_secret，以 Webhook 同步状态，复用原有 Session 处理失败，并按隐私要求管理脱敏和本地数据副本。

产品文案要清楚区分“已提交”“处理中”“验证通过”和“需要补充资料”。不要把技术失败等同于身份不实，也不要保存不必要的身份证明数据。更多细节请核对 [Stripe Verification Sessions API 指南](https://docs.stripe.com/identity/verification-sessions)、[验证类型说明](https://docs.stripe.com/identity/verification-checks) 和 [用户身份文件验证流程](https://docs.stripe.com/identity/verify-identity-documents)。
