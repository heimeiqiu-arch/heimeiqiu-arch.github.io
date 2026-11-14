---
title: "Stripe Coupon 与 Promotion Code 怎么配置？订阅折扣、限制与结账验证"
date: 2026-11-14
description: "Stripe Coupon 和 Promotion Code 使用指南：理解折扣持续时间、客户与兑换限制、Checkout/订阅应用方式，排查优惠码无效和金额不符。"
slug: stripe-coupon-promotion-code-subscription-discount-guide
tags:
  - Stripe
  - Coupon
  - Promotion Code
  - 订阅折扣
  - Checkout
keywords:
  - Stripe Coupon
  - Stripe Promotion Code
  - Stripe 优惠码
  - Stripe 订阅折扣
  - promotion_code限制
---

# Stripe Coupon 与 Promotion Code 怎么配置？订阅折扣、限制与结账验证

在 Stripe 订阅和 Checkout 场景中，Coupon 与 Promotion Code 经常被统称为“优惠码”，但两者承担的角色不同：Coupon 定义优惠规则，Promotion Code 提供客户可以输入或使用的代码，并可以附加兑换限制。理解这一层关系后，商家更容易配置折扣持续时间、限定客户、设置兑换上限，也能排查客户输入代码后为什么看不到预期价格。

本文介绍 Stripe 优惠对象的基本关系、适用于一次性付款和订阅的策略、Dashboard/API 核对方法、常见兑换限制和上线测试。优惠规则可能影响退款、税费、收入确认和客户合同，正式上线前应让财务与产品团队确认宣传口径和实际账单行为。

## Coupon 和 Promotion Code 的关系

可以把 Coupon 理解为折扣方案，把 Promotion Code 理解为客户使用的入口代码。一个 Coupon 可以对应不同的 Promotion Code；不同代码可以有各自的过期时间、客户限制或兑换上限，但最终应用的是它所关联的 Coupon 折扣。

Coupon 常定义：

- 折扣方式：百分比折扣或固定金额减免；
- 折扣持续时间：只应用一次、重复若干个月或持续有效；
- 总兑换次数上限（若设置）；
- 适用的产品或价格范围（若配置）；
- 货币与其他折扣参数。

Promotion Code 可定义：

- 客户看见或输入的代码；
- 是否只对某个 Customer 生效；
- 最多可兑换次数；
- 代码的有效期；
- 首次交易限制或最低金额等限制（以当前 API 能力为准）。

Promotion Code 对象引用 Coupon；订单实际折扣则会以 Discount 形式关联到客户、订阅或 Invoice。排查优惠时要看完整对象链路，不能只查用户输入的字符串。

## 选择折扣持续时间

订阅 Coupon 常见的持续时间包括：

- **once：** 只对首次相关收费应用一次；
- **repeating：** 在设置的持续月份内应用；
- **forever：** 在适用对象的持续期间内持续应用。

业务文案应该准确描述优惠作用范围。例如“首期减免”与“前 3 个月折扣”并不是同一承诺。一次性 Coupon 与 Promotion Code 的有效期也不同：代码何时能兑换，与已兑换客户的折扣持续多久，是两个时间概念。

上线前列出实际账单例子：首期金额、之后每期金额、优惠结束日期、税费如何计算、是否包含一次性费用、升级或降级后折扣如何处理。不要只在商品页写“立减 20%”而不说明是首笔、周期内还是整个订阅期间。

## 创建时先决定限制规则

优惠码很容易被截图分享，因此要提前明确：

1. 是否公开给所有客户，还是仅针对某个 Customer；
2. 代码是否有截止时间；
3. 总兑换数和每个客户的使用范围；
4. 是否限制为首次交易或达到最低消费；
5. 是否仅适用于指定产品或价格；
6. 客户能否把代码用于已有订阅；
7. 是否能与其他优惠叠加；
8. 取消后重新订阅是否还能使用。

如果优惠只给特定客户，使用客户绑定限制比依赖前端隐藏代码更可靠。前端展示条件只是用户体验；真正的可用性应由 Stripe 对象限制和服务端业务规则控制。

对大型公开活动，应关注 Promotion Code 的 `active`、`expires_at`、`max_redemptions`、`times_redeemed` 和 `restrictions` 等信息。达到兑换上限或超过有效期后，客户应看到明确提示并获得当前可用的价格，而不是进入支付后才发现优惠失效。

## 在 Checkout 中允许客户输入代码

Checkout Session 是否允许 Promotion Code 输入，取决于 Session 创建方式和产品配置。创建 Session 时应启用相应的促销代码选项，并确认当前模式及优惠对象兼容。若结账页面有优惠输入框，客户输入后应在最终付款前看到更新后的金额和订单摘要。

服务端不要根据浏览器提交的折扣数值自行算出应付金额。正确做法是将 Promotion Code 的 ID 或代码交由 Stripe 规则验证，或在商家后端核对可用性，再按支持方式创建或更新 Checkout Session。客户端显示的价格不能作为资金扣款依据。

测试 Checkout 时，检查：

- 输入有效代码后折扣确实应用；
- 无效、过期或已达上限代码有可理解的错误提示；
- 不支持的产品、币种或客户无法绕过限制；
- Session 中行项目金额与订单快照一致；
- 支付成功后的 Invoice 显示了正确 Discount；
- 客户收到的确认邮件和账单摘要与结账页一致。

## 订阅中的折扣应用

订阅折扣可以在创建订阅时应用，也可以通过允许的流程更新现有订阅。已应用的优惠会影响后续 Invoice，折扣结束时应恢复到原定价或按当前订阅规则继续收费。对已有客户应用优惠时，先确定影响未来账单还是当前未付 Invoice，再核对 Stripe 返回的 Discount 和 Invoice line items。

如果允许客户在 Customer Portal 中变更订阅或输入 Promotion Code，应该检查门户配置是否支持相关更新，并限定可切换的产品和 Price。升级和降级可能同时产生 proration；优惠如何作用于调整金额要结合当前规则测试，不能只按原月费比例推算。

特别注意这些场景：

- 订阅折扣与产品 Price 级别折扣同时存在；
- Customer 上已有 Coupon，创建新订阅时继承或覆盖；
- 一次性 Invoice item 是否享受订阅折扣；
- 客户升级、降级、调整数量或账期时的折扣适用范围；
- 试用结束后首个付费周期是否仍有优惠；
- 订阅取消后重新开通是否会再获得新客优惠。

复杂场景建议用 Invoice Preview 检查下期金额，在实际变更前对照预期。对高价值合同，不应仅依赖促销码自动续费逻辑，必要时在业务系统中记录批准的优惠版本和截止时间。

## 代码大小写和客户体验

Promotion Code 的代码字符串通常需要遵守 Stripe 的格式和唯一性规则。不要在自己的营销系统中把代码大小写转换、截断或添加空格后，再错误地拿转换结果当作不同优惠。客户输入时可以在前端做空白清理，但必须将规范化行为与 Stripe 当前的代码规则保持一致。

代码应易于输入且不容易混淆，例如避免难以区分的字符组合。错误提示可以区分“代码无效”“已过期”或“当前购物车不适用”，但不要泄露其他客户绑定的促销码是否存在。客服后台应根据 Promotion Code ID 和对象状态查询，而不是从客户的一张截图判断优惠已生效。

## API 与运营管理

通过 API 建立优惠时，建议先创建 Coupon，再创建关联的 Promotion Code。不同对象的生命周期和限制字段不同，不能只修改 Coupon 就假设客户代码的有效期也自动改变。查询优惠码时可以按 code、coupon、active 等条件过滤，并对大规模列表使用分页。

运营管理可以保存如下信息：

- 内部促销活动 ID；
- Stripe Coupon ID 和 Promotion Code ID；
- 活动开始与结束时间；
- 宣传文案版本；
- 适用产品、Price、国家或客户群；
- 兑换上限和使用数据；
- 审批人、成本预算和停用原因；
- 测试模式与真实模式对象的映射。

优惠活动结束时，应确认需要停用的是客户输入代码、底层 Coupon，还是所有关联优惠。提前计划停用流程，可以避免促销页面已经结束但代码仍可使用，或客户在活动期间打开旧页面后错误地失去优惠。

## 常见问题排查

### 客户输入代码后提示无效

核对代码是否存在、是否 active、是否过期、是否达到 max redemptions，是否绑定特定客户或有最低金额/首次交易限制。再确认所购产品和币种符合 Coupon 与 Promotion Code 的规则。

### Coupon 有效但 Checkout 不显示优惠框

检查创建 Checkout Session 时是否启用了 Promotion Code 输入，当前 Checkout 模式是否适用，及是否已经通过 Session 固定了另一个优惠方案。

### 代码已使用，但账单金额没有变化

查看 Checkout Session、订阅、Discount 和 Invoice line items，确认优惠究竟应用在哪个对象。也要留意只在首期或指定月份生效的 Coupon，后续账单回到原价可能是预期行为。

### 同一个客户反复创建账户获得新客折扣

Stripe 的首次交易限制依据 Stripe 可验证的数据和规则，不应被当成可以替代商家身份系统的完整反滥用方案。若业务需要防止多账户重复使用首客优惠，还应使用合规的账户验证、业务规则和风险评估，不要仅依赖前端邮箱比较。

### 活动已结束但仍有人兑换

检查 Promotion Code 的过期时间和 `active` 状态，以及是否另外存在绑定相同 Coupon 的其他代码。停止一条 Promotion Code 不一定等于全局停用所有相关优惠。

## 总结

Stripe Coupon 定义折扣本身，Promotion Code 提供客户使用该折扣的代码和额外限制。配置时要分别设计折扣方式与持续时间、代码兑换期限、客户绑定、总兑换数和最低金额等规则。订阅折扣还需要验证首期、续费、升级、降级、试用结束及取消后重开等实际账单结果。

在 Checkout 或 Customer Portal 中允许输入优惠码之前，先在服务器端确定适用范围，再用测试模式验证有效、过期、超限和不适用情形。通过保存 Stripe 对象 ID、活动文案版本与兑换记录，商家可以更准确地答复客户、控制优惠成本，并避免结账金额和营销承诺不一致。

## 官方资料

- [Stripe 优惠和 Coupon 指南](https://docs.stripe.com/billing/subscriptions/coupons)
- [Stripe Promotion Code 对象和 API](https://docs.stripe.com/api/promotion_codes)
- [Stripe Discount 对象](https://docs.stripe.com/api/discounts)
- [Stripe Invoice 对象中的折扣字段](https://docs.stripe.com/api/invoices/object)
- [Stripe Customer Portal 配置](https://docs.stripe.com/customer-management/configure-portal)
