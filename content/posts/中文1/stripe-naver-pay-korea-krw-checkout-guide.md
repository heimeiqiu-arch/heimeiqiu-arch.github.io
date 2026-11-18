---
title: "Stripe Naver Pay 接入指南：韩国客户、KRW 币种与跳转支付"
date: 2026-11-15
slug: "stripe-naver-pay-korea-krw-checkout-guide"
description: "介绍 Stripe Checkout 接入 Naver Pay 的账户地区和 KRW 要求、跳转授权流程、Naver Pay Points、动态支付方式及测试注意事项。"
keywords:
  - Stripe Naver Pay
  - Naver Pay Stripe 接入
  - 韩国 KRW 收款
  - Stripe Checkout 韩国支付
  - Naver Pay 测试
tags:
  - Naver Pay
  - 韩国支付
  - Checkout
---

面向韩国消费者销售商品或数字服务的商家，除了银行卡，还可以评估 Naver Pay 这类本地钱包支付方式。Stripe Checkout 的 Naver Pay 流程会将客户引导到本地支付处理方完成身份验证和付款授权，再把客户带回商家网站。客户还可以选择使用 Naver Pay Points 支付购买金额的一部分或全部，具体方式以支付页面为准。

接入前最重要的是确认账户资格和币种：Stripe 当前文档要求所有 Checkout line item 使用 KRW，Naver Pay 的展示币种也是 KRW。即使商家网站支持多币种，也不能在同一个 Checkout Session 中把该方式当作任意币种的通用钱包。本文梳理账户地区、Checkout 设置、跳转处理和测试事项，帮助团队判断 Naver Pay 是否适合目标客户。

## Naver Pay 的付款体验

客户在 Checkout 选择 Naver Pay 后，会跳转到支付合作方页面完成身份验证与授权。授权成功后，用户返回商家网站。因为这是跳转型支付，浏览器离开商家页面并不代表订单已付款；用户可能取消、关闭页面或遇到网络中断。商家应通过服务端 Stripe 状态和 webhook 确认交易，再发货或开通数字服务。

客户可以选择用 Naver Pay Points 参与支付。平台应确保订单确认页、邮件和财务对账以 Stripe 最终金额和币种为准，不要依据客户点击支付前的商品小计自行推断支付结果。若客户使用积分，结账体验和资金明细可能由钱包侧呈现；客服应能通过内部订单号和 Stripe PaymentIntent 找到对应交易。

## 商家账户地区与币种要求

Stripe 当前 Naver Pay Checkout 文档列出可用的商家账户国家和地区，其中包括部分欧洲国家、英国、日本、香港、新加坡和美国等。实际可用性依赖 Stripe 账户国家和 Dashboard 当前显示，不能仅根据客户身处韩国或网站可收韩元推断账户已经具备该付款方式。

Stripe 文档当前要求：

- Checkout 所有 line_items 的价格都使用 KRW；
- Naver Pay 的展示币种为 KRW；
- 最低接受金额为 100 KRW；
- 文档说明卡片直通类交易没有同样的金额上限，但客户向 Naver Pay 账户储值的上限为 2,000,000 KRW；
- 可用于一次性付款、Setup 模式和订阅模式，具体需按账户和集成方式验证。

金额上限的表述容易引起误解：卡片交易与钱包储值不是同一个资金路径。商家不应把某个储值限制误当成所有交易的统一最大金额，也不应自行假设任意交易金额都必然通过。应在测试环境和实际 Dashboard 配置中确认项目适用规则，并以 Stripe 当前文档为准。

## 使用 Checkout 启用 Naver Pay

商家可在 Stripe Dashboard 支付方式设置中启用 Naver Pay。如果现有集成使用 Stripe 动态支付方式，Stripe 可根据结账上下文决定是否向符合条件的客户显示该方式。若集成手动指定 payment_method_types，则开发团队需要检查迁移建议和当前 API 配置，避免新支付方式没有被纳入允许列表。

创建 Checkout Session 时，后端应确认所有商品行均为 KRW，并按项目使用的 Checkout UI 模式提供正确的返回 URL 或 success_url。标准托管页面、嵌入式 Checkout 或其他 UI 的 API 字段可能不同，不能复制某个模式的请求参数到另一个模式。

上线前建议让用户在明确显示韩元价格的页面进入 Checkout。若一个购物车中包含多种币种的价格，应先在商家服务端按预定规则统一币种，或阻止用户继续创建不兼容的 Session。不要把客户端传来的金额直接用作 Stripe 价格；后端应从可信产品目录读取 Price 和币种。

## 订阅与 Setup 场景要单独验证

Stripe 文档列出 Naver Pay 可用于订阅模式和 Setup 模式。对订阅业务而言，团队要分别测试首次付款、后续续期、付款失败和客户取消。不要因为首期跳转授权成功，就假设未来每个账期都与银行卡自动扣款行为完全相同。可用付款方式、客户授权和交易状态应根据 Stripe 返回的订阅、发票及付款对象处理。

Setup 场景可以用于建立后续付款关系，但商家应确认客户授权内容、支付方式是否可复用以及未来扣款所需条件。条款页面应说明收费频率、扣款时间、取消方式和退款政策。任何重复收费都要符合客户明确授权和业务所在地的规则。

## 支付状态与订单履约

Naver Pay 的跳转流程可能让前端页面返回时间和服务端支付状态更新不同步。建议订单系统使用“等待客户授权”“处理中”“支付成功”“支付失败”“已取消”等状态。客户返回网站时显示“正在确认支付”并向后端查询订单，而不是立即触发发货。

Webhook 处理应：

1. 验证 Stripe 签名并确认测试或生产环境；
2. 根据事件 ID 做幂等去重；
3. 将 PaymentIntent、Checkout Session 与内部订单号关联；
4. 读取当前支付状态和币种、金额；
5. 仅在确认付款成功后执行履约；
6. 记录失败、取消和重复回调，方便客服排查。

支付成功页应该是用户体验的一部分，不是支付真相的唯一来源。如果用户在授权后没有返回成功页，后台仍可能收到成功事件；如果用户返回页面但支付尚未完成，后端也不能将订单标记为已付。

## 测试重定向型支付方式

Stripe 文档说明，在测试 Checkout 中选择 Naver Pay 后，测试流程会跳转到 Stripe 提供的测试页面，允许开发者模拟授权成功或付款失败。授权成功时，PaymentIntent 会从 requires_action 变成 succeeded；测试失败则从 requires_action 转为 requires_payment_method。

建议覆盖这些案例：

- 授权成功后返回商家页面；
- 客户在钱包流程中取消；
- 测试授权失败；
- 用户完成授权后关闭标签页；
- Stripe webhook 延迟或重复投递；
- 订阅首期付款与续费状态；
- 价格不是 KRW 时阻止创建 Checkout；
- 小于最低金额的订单被业务层拒绝；
- 移动端和桌面端的跳转及返回路径。

另外，Stripe 指出商家网站展示 Naver Pay 品牌时必须遵守其品牌指南。按钮、标识、文案和合作方描述应按 Naver Pay 官方规范使用，不要随意改变 Logo 或暗示商家与 Naver 之间存在未经批准的合作关系。

## 常见接入错误

**账户能服务韩国客户就认为可以用 Naver Pay。** 付款方式有商家账户国家范围，需在 Dashboard 确认。

**Checkout Session 混用其他币种。** 所有 line item 应为 KRW；多币种购物车要先处理转换或拆分逻辑。

**使用固定的订阅经验推断续费。** Setup、一次性和订阅模式应分别测试。

**跳转回来就认为付款成功。** 后端需通过 Stripe 对象和事件确认状态。

**忽略客户使用积分的可能性。** 客户支付金额和资金流应以最终 Stripe 记录为准，客服应能解释订单与钱包体验。

**只测试成功路径。** 还要测试失败、取消、页面关闭、Webhook 重试和异常币种。

## 上线清单

- Stripe Dashboard 已为目标账户启用 Naver Pay；
- 商家账户国家符合当前资格；
- Session 中每项 Price 均为 KRW；
- 最低金额和交易类型限制符合当前文档；
- 目标 Checkout UI 使用正确的返回配置；
- 订阅和 Setup 场景已经分别验证；
- Webhook 签名、幂等和订单关联正确；
- 支付成功后才履约；
- 取消和授权失败有清晰订单状态；
- 网站品牌元素符合 Naver Pay 品牌指南；
- 客服能够按订单号查询 Stripe 状态与币种。

## 总结

Stripe Naver Pay 适合希望为韩国客户提供 Naver 钱包体验的商家，但账户资格和 KRW 币种约束必须先确认。客户会跳转到支付流程中完成授权，也可能使用 Naver Pay Points，因此页面返回不能代替服务端付款确认。一次性付款、Setup 和订阅需要分别测试。

上线时要使用动态支付方式或正确配置手动支付方式列表，验证失败和取消路径，并遵循 Naver Pay 品牌规范。通过 Dashboard、Checkout Session 和 webhook 的端到端检查，才能确保韩国客户看到正确价格，商家后台也只在确认付款后履约。

## 参考资料

- [Stripe：使用 Naver Pay 的 Checkout 接入指南](https://docs.stripe.com/payments/naver-pay/accept-a-payment?payment-ui=checkout)
- [Stripe：Naver Pay Direct API 接入说明](https://docs.stripe.com/payments/naver-pay/accept-a-payment?payment-ui=direct-api)
- [Stripe：动态支付方式](https://docs.stripe.com/payments/payment-methods/dynamic-payment-methods)
- [Naver Pay 品牌指南](https://developers.pay.naver.com/design/brand/overseas)
