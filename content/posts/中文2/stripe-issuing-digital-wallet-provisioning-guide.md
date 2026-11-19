---
title: "Stripe Issuing 数字钱包指南：Apple Pay、Google Pay 与推送开卡"
date: 2026-11-19
slug: "stripe-issuing-digital-wallet-provisioning-guide"
description: "介绍 Stripe Issuing 卡片手动添加与 Push Provisioning 的差异，梳理钱包资格检查、Apple 审批、Cardholder 联系方式和无法使用 Sandbox 测试等注意事项。"
keywords:
  - Stripe Issuing Apple Pay
  - Stripe Issuing Google Pay
  - Push Provisioning
  - Stripe 数字钱包开卡
  - Issuing 钱包资格
tags:
  - Stripe
  - Issuing
  - Apple Pay
  - Google Pay
  - 数字钱包
---

# Stripe Issuing 数字钱包指南：手动添加、Push Provisioning 与资格检查

Stripe Issuing 卡片可以加入 Apple Pay、Google Pay 等数字钱包。持卡人可以自己在手机钱包应用中输入卡片资料，也可以从发卡企业的 App 或网站点击“添加到钱包”，由应用启动 Push Provisioning 流程。两种方式都需要正确的卡片、持卡人信息和钱包平台批准，但工程工作量和用户体验不同。

一个特别重要的限制是：Stripe 官方说明 Issuing 数字钱包 token 只能在 Live 模式使用，无法在 Sandbox 中完整测试。要测试钱包 token，项目必须获准用于 Live 场景并使用真实卡片。因此，不能把普通 Sandbox 付款通过当成 Wallet Provisioning 已可上线的证明；应提前规划项目审批、真实设备验证和内部风险控制。

## 一、手动添加和 Push Provisioning 的区别

**手动添加**由持卡人打开 Apple Wallet、Google Wallet 或其他受支持钱包，输入实体卡或虚拟卡信息。Stripe 会向与该 Cardholder 关联的手机号或邮箱发送验证码。商家不需要在自己的 App 中构建“添加到钱包”按钮，但必须确保 Cardholder 的联系方式完整且可接收验证码。如果手机号和邮箱都缺失，钱包可能显示卡片不受支持。

**Push Provisioning**让持卡人从商家的 App 或网站直接把卡片加入数字钱包。用户点击按钮后，商家应用调用相应钱包平台的流程，减少手动输入。实现需要针对每个平台进行代码集成，并取得 Stripe 及钱包平台所需批准。Apple Pay 的 iOS 推送开通涉及 Apple entitlement；不同操作系统、SDK 和钱包的要求并不相同。

手动添加适合先建立基本钱包支持的项目；Push Provisioning 适合希望将钱包入口嵌入 App、提供更顺畅开卡体验的项目。平台可以先满足手动添加的资格，再逐步实现 push flow，但不能把一个平台的批准自动当作另一个平台也已获批。

## 二、卡片和 Cardholder 资料检查

钱包使用的是卡片的 tokenized representation，而不是把实体卡或虚拟卡对象直接复制进手机。钱包 token 与 Issuing Card 是不同对象，生命周期和状态需要分开理解。卡片被冻结或取消、钱包 token 状态变化以及设备中的钱包展示，可能需要通过不同流程处理。

开始前确认：

- Card 对象处于可用状态，卡片类型和项目支持目标钱包；
- Cardholder 关联了有效手机号或邮箱，用于手动添加时的验证码；
- 账户的 wallet eligibility 字段显示目标钱包可用；
- 国家、卡网络和 Stripe 项目权限符合当前产品要求；
- 对应 Apple、Google 或其他钱包的批准已完成；
- 应用已按官方要求使用对应平台 SDK 和版本。

不要仅根据设备可以使用 Apple Pay，就推断某张 Issuing 卡可以加入 Apple Wallet。项目资格、卡片数据、账户审批、设备地区和持卡人状态都可能影响结果。

## 三、Apple Pay 推送开通的资格检查

Stripe iOS 文档要求在显示 Add to Apple Wallet 按钮前检查服务端卡片资格和设备资格。后端读取 Issuing Card 中 Apple Pay eligible 状态及 primary account identifier，并把必要数据安全传给 iOS 应用；客户端再调用 PassKit 的设备检查方法，确认设备能够添加该卡。

两个条件必须都成立，才应展示系统提供的 Add to Apple Wallet 按钮。如果仅显示按钮而没有执行资格检查，Apple App Review 可能拒绝应用。若 primary account identifier 为空，也应按 Stripe 文档规定的方式处理，而不要自行假设该卡不可用或无限制。

iOS Push Provisioning 需要 Apple 的 payment-pass-provisioning entitlement。申请时 Stripe 文档要求提供卡网络、钱包展示卡名、App 名称、Apple Developer Team ID、App Store Connect 中的 App ID 和 Bundle ID。多个应用如测试版和正式版的这些字段不同，可能需要分别申请。团队还应将 entitlement 和 Stripe 批准纳入发布清单，避免只在开发者本地配置而未包含生产 App。

## 四、不同国家和钱包的启用差异

数字钱包启用方式随地区和钱包供应商变化。Stripe 文档指出，美国和加拿大的 Apple Pay Issuing 钱包需要 Apple 批准，Dashboard 设置中可以查看状态；申请提交后可能需要等待审批。Google Pay 和 Samsung Pay 在该地区的手动添加没有额外启用步骤。欧洲和英国的数字钱包集成需要 Stripe 合作团队审批，Apple Pay 还可能需要额外的 Apple 批准。

这些要求会根据 Stripe Issuing 项目和钱包政策调整。不要把其他国家或账户的结果当成自己的资格。项目经理应在开发计划前确认每个目标国家、卡网络、平台应用和钱包类型的状态，并将审批时间纳入时间表。资格未明确时，应用界面应隐藏不可用的添加入口，并保留手动添加或普通卡片使用的清晰说明。

## 五、为什么 Sandbox 不能验证真实钱包 token

Stripe 官方说明，数字钱包 token 仅用于 Live 模式，Sandbox 无法测试这一功能。需要进行钱包 token 测试的项目，应先获准用于 Live 使用场景，并使用真实卡片。这意味着普通模拟交易无法覆盖设备钱包的完整发卡、验证和 token 化流程。

项目应把两种测试分开：Sandbox 用于验证卡片创建、持卡人关联、授权事件和应用业务逻辑；获准后的受控 Live 测试用于检查真实设备的钱包添加体验。真实测试应使用经批准的内部卡片、测试持卡人流程和受控金额，不要用客户卡片做未经同意的实验。

如果钱包添加失败，记录卡片对象、账户资格、设备型号、操作系统、钱包应用、时间和错误提示，再判断问题来自 Stripe entitlement、wallet eligibility、卡片状态、Cardholder 验证，还是钱包平台本身。切勿为了排错而在正式应用中移除资格检查或通过前端参数伪造 eligible 值。

## 六、生产系统和客服流程

钱包加入成功后，客服仍需要将手机钱包使用与 Issuing Card 关联起来。不要保存完整钱包 token 或在普通客户日志中记录敏感卡片数据。可以根据 Stripe 对象展示合适的卡片末四位和品牌，并提供卡片冻结、遗失、设备更换和解绑指引。

持卡人更换手机、设备丢失或卡片被盗时，处理逻辑可能涉及冻结 Issuing Card、联系钱包提供商或发出替换卡。钱包中的 token 与物理卡可能需要不同的操作步骤。客服知识库应说明什么情况下应先冻结卡、何时取消卡、如何重新发行，以及如何确认旧设备或旧 token 不再可用于新付款。

## 七、上线检查清单

1. 在 Stripe Dashboard 确认 Issuing 数字钱包项目已获准。
2. 逐个地区、卡网络和钱包检查支持状态，不假设全球一致。
3. 确保 Cardholder 有可用手机号或邮箱，便于手动添加验证。
4. 在服务端读取钱包 eligible 标志，客户端完成设备资格检查。
5. 未满足资格时不展示 Push Provisioning 按钮。
6. 完成 Apple entitlement 和平台级审批，并核对 App ID、Team ID 与 Bundle ID。
7. 对 Android、iOS、React Native 或 Web 分别采用相应官方集成流程。
8. 规划 Sandbox 逻辑测试与获准后的受控 Live 钱包测试。
9. 为设备更换、卡片遗失、冻结和重新添加建立客服流程。
10. 不记录完整卡片数据、密钥或钱包 token，保护持卡人信息。

## 总结

Stripe Issuing 数字钱包支持手动添加和 Push Provisioning 两类体验。手动添加依赖持卡人资料和钱包验证码；Push Provisioning 则需要应用集成、设备资格检查和钱包平台审批。项目应根据国家、卡网络和钱包分别确认可用性，并在显示“添加到钱包”按钮前完成资格判断。

数字钱包 token 不能在 Sandbox 中完整测试，是安排上线计划时必须考虑的限制。通过 Sandbox 测试普通卡片业务，再在获得批准后使用受控的 Live 卡片验证实际钱包流程；同时将卡片和钱包 token 的状态、客服处理与敏感信息保护分开管理。

## 官方参考资料

- [Stripe Issuing 数字钱包总览](https://docs.stripe.com/issuing/cards/digital-wallets)
- [Stripe Issuing iOS 钱包开通流程](https://docs.stripe.com/issuing/cards/digital-wallets?platform=ios)
- [Stripe Issuing Android 钱包流程](https://docs.stripe.com/issuing/cards/digital-wallets?platform=android)
- [Stripe Issuing 网络令牌管理](https://docs.stripe.com/issuing/controls/token-management)
