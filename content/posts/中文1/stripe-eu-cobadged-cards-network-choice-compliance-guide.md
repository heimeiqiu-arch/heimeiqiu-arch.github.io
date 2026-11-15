---
title: "Stripe 欧盟联名银行卡指南：Cartes Bancaires 网络选择与集成合规"
date: 2026-11-15
slug: "stripe-eu-cobadged-cards-network-choice-compliance-guide"
description: "解释欧盟联名银行卡的消费者网络选择要求，梳理 Stripe Checkout、Payment Element、Card Element 和 Direct API 的集成差异与上线检查。"
keywords:
  - Stripe 联名银行卡
  - co-badged cards compliance
  - Cartes Bancaires Stripe
  - 欧盟银行卡网络选择
  - Stripe Payment Element 合规
tags:
  - Stripe
  - 卡片支付
  - 欧盟支付
  - Cartes Bancaires
  - Payment Element
---

# Stripe 欧盟联名银行卡指南：网络选择和集成合规

在欧洲，消费者可能持有同时带有多个支付网络标识的银行卡，例如法国本地 Cartes Bancaires 与 Visa 或 Mastercard 联名的卡片。付款时，交易可能可以通过不同网络处理。Stripe 的 co-badged cards 文档说明，相关欧盟规则要求在使用联名卡付款时，让消费者能够选择偏好的卡网络。具体要做什么取决于商家采用的 Stripe 集成方式。

这项要求很容易被误读为“所有商家都必须手工开发一个卡网络下拉菜单”。Stripe 当前说明指出，Checkout、Payment Links 和 Payment Element 等托管界面符合文档所列要求，一般无需商家另外操作；如果使用 Card Element 或直接 API 集成，则可能要迁移到推荐的托管组件或自行实现相应的展示与选择。第一步应准确识别线上、移动端和线下每条支付路径，而不是只看网站主结账页。

## 一、什么是联名卡和网络选择

联名卡具有多个支付网络品牌或应用。例如一张银行卡既带有本地网络，也带有国际卡组织标识。客户在付款时需要按适用规则能够选择偏好的网络，最终交易则应按所选择或适用的网络完成。对商家而言，正确处理这一选择有助于兼容当地支付要求，也让客户清楚付款经过哪个网络。

Stripe 对卡对象提供如 display_brand 或网络相关信息字段，供不同支付功能使用；具体字段和场景依赖 API 对象与集成产品。商家不应仅根据卡片正面可见的一个标志，自己推断底层实际处理网络，也不应在客户选择之后用另一网络静默覆盖其选择。

法国 Cartes Bancaires 是常见的联名网络场景。Stripe 介绍，许多 Cartes Bancaires 卡片还与 Visa 或 Mastercard 联名。对受该规则影响的欧洲交易，商家需要确认自己选择的 Stripe 集成如何呈现网络选择，以及结账最终使用什么网络。

## 二、不同 Stripe 集成的要求不同

### Checkout 和 Payment Links

Stripe 的帮助中心说明，使用 Stripe Checkout 或 Payment Links 时无需采取额外操作；托管界面已覆盖相应要求。商家仍要确保正在使用当前受支持的集成版本，并遵守官方迁移和产品更新要求。若使用自定义支付页包装 Checkout，确认自定义页面没有隐藏、遮挡或错误呈现 Stripe 托管界面中的卡片网络选择信息。

### Payment Element

Stripe 当前对 Payment Element 的说明同样列为无需额外操作。Payment Element 管理相应的卡网络体验，商家应使用官方组件与受支持的配置，而不是自行覆盖卡品牌展示或屏蔽组件提供的交互。若前端应用自定义样式，检查不同屏幕尺寸和联名卡测试流程，确保网络选择提示仍然可见。

### Card Element

Stripe 帮助中心对 Card Element 的说明建议优先迁移到 Payment Element，并要求确认集成显示卡片图标。旧版 Card Element 的具体实现可能需要更新显示选项。若暂时无法迁移，应按 Stripe 对该组件的专门合规文档确认所需行为，并在上线前测试实际联名卡场景。

### Direct API 或自建卡片表单

如果商家绕过 Stripe 托管界面，使用直接 API 或自行制作的卡片表单，Stripe 帮助中心说明需要更新集成以呈现选择器。自建流程意味着商家需要确保客户能够看到并选择可用的网络，然后将选择正确传入支付请求。不能只在说明文档中写有“可选择网络”，界面却没有实际选择方式。

对自建集成，先审查从卡片识别、网络展示、客户选择、支付确认到交易回执的完整流程。明确未出现选择条件时如何处理、选择值何时锁定、失败后重试是否保留原网络，以及客户修改卡号时是否重新识别。所有 API 参数应依当前 Stripe 合规文档确认，避免使用过时字段或自定义枚举。

## 三、审查线上、移动端和 Terminal 的每条路径

同一家企业可能同时使用网站 Checkout、移动端 Payment Sheet、Card Element、Terminal 和第三方电商插件。每种界面都应分别核对，因为一个已合规的 Checkout 页面无法自动保证另外的自建流程也合规。

Stripe 的 co-badged cards 文档提供了 Checkout、Payment Links、Web Elements、Mobile Elements 和 Terminal 的不同说明入口。工程团队应根据实际集成种类查看相应变体：例如 iOS 或 Android Payment Sheet 与网站 Payment Element 属于不同界面；Terminal 也有自己的说明，不能套用网页规则。

若使用第三方插件，应核实插件版本及其维护方的合规说明。Stripe 帮助中心指出 Stripe 自有 Connector 默认符合要求，但商家仍需更新到最新插件版本。自行修改插件代码、隐藏默认卡片图标或增加支付拦截逻辑后，应重新核对实际行为。

## 四、升级和验证步骤

可按以下流程完成集成审查：

1. 列出生产环境中的所有收款渠道和卡片组件，包括桌面网站、移动端、插件和 Terminal。
2. 为每条路径标明 Checkout、Payment Links、Payment Element、Card Element 或 Direct API。
3. 打开 Stripe 对应集成类型的 co-badged cards 说明，确认该路径当前要求。
4. 对无需额外操作的托管界面，确认组件版本、样式和显示行为没有被自定义代码破坏。
5. 对 Card Element 检查卡片品牌图标显示，并评估迁移到 Payment Element。
6. 对 Direct API 集成实现客户选择器，按 Stripe 文档传递选择并保存相关交易信息。
7. 在测试环境构造或使用适用的联名卡场景，验证选择可见、提交后网络选择一致、错误时可恢复。
8. 检查移动端无障碍、键盘操作、屏幕阅读器提示和多语言文案。
9. 记录负责团队、插件版本、Stripe API 版本、测试日期和生产发布记录。
10. Stripe 更新要求或更换支付组件时重新审查。

## 五、常见错误和排查方向

**只在卡片品牌图标旁显示一个标志，没有客户选择。** 若使用 Direct API 或自建表单，确认当前 Stripe 文档要求的选择器是否已实现。图标展示与客户选择是不同功能。

**商家已使用 Stripe，但仍自行接管网络选择。** 托管组件已经提供相关体验时，自行覆盖可能产生行为差异或破坏合规交互。优先使用 Stripe 当前推荐的界面，避免无必要地重复实现。

**Desktop 正常，Mobile 不显示选择提示。** 检查移动端使用的 Payment Sheet、Payment Element 或其他组件变体，而不是只测试网页。不同平台需分别按其集成文档验证。

**插件更新后样式被覆盖。** 检查主题 CSS、第三方脚本和插件版本是否隐藏了卡片图标或组件内控件。更新后使用代表性的联名卡流程重新测试。

**交易数据中网络品牌和客户选择不一致。** 确认客户选择值是否正确传递到 Stripe、最终支付对象显示的网络字段代表什么，以及支付状态是否来自服务端对象。不要只凭前端界面记录判断交易实际网络。

## 六、上线检查清单

- 已盘点全部网站、移动端、Terminal 和第三方插件支付入口。
- 每条路径都匹配了 Stripe 官方 co-badged cards 文档变体。
- Checkout、Payment Links 和 Payment Element 使用受支持界面并保留相关展示。
- Card Element 已按要求显示图标，或有明确迁移计划。
- Direct API 集成实现实际可操作的网络选择器。
- 联名卡流程在测试环境验证选择、支付和错误恢复。
- 手机屏幕、辅助技术和多语言文案已经检查。
- 插件和 Stripe API 版本纳入定期更新管理。
- 生产发布记录能追溯组件、测试和责任团队。
- 对地区规则变化建立合规复核提醒，并咨询适用的法律或合规负责人。

## 总结

欧盟联名银行卡的网络选择要求，不能用一个“一刀切”的实现覆盖所有 Stripe 集成。Stripe 当前说明将 Checkout、Payment Links 和 Payment Element 列为无需额外操作；Card Element 需要检查卡片图标展示并优先考虑迁移；Direct API 则需由商家实现选择器。移动端、Terminal 和第三方插件也要分别核对相应文档。

商家应先盘点真实支付路径，再逐一匹配 Stripe 的官方指南。不要自行推断卡品牌或隐藏用户选择，也不要假定网站托管页面的合规能力自动覆盖自建组件。保留集成版本和验证记录，并在支付界面或法规发生变化时及时复查。

## 官方参考资料

- [Stripe 联名卡合规文档总览](https://docs.stripe.com/co-badged-cards-compliance)
- [Stripe 关于联名银行卡的要求](https://support.stripe.com/questions/requirements-for-accepting-co-badged-cards)
- [Stripe Payment Element](https://docs.stripe.com/payments/payment-element)
- [Stripe Cartes Bancaires 说明](https://stripe.com/payment-method/cartes-bancaires)
