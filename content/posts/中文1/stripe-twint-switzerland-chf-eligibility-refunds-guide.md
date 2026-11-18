---
title: "Stripe TWINT 接入指南：瑞士 CHF 支付与商家网站审核"
date: 2026-11-15
slug: "stripe-twint-switzerland-chf-eligibility-refunds-guide"
description: "介绍 Stripe TWINT 的瑞士客户与 CHF 结账要求、商家网站审核条件、账户资格、支付限额、退款窗口和 Connect 使用注意事项。"
keywords:
  - Stripe TWINT
  - TWINT Stripe 接入
  - 瑞士 CHF 收款
  - Stripe 瑞士支付方式
  - TWINT 退款
tags:
  - TWINT
  - 瑞士支付
  - Checkout
---

TWINT 是瑞士消费者使用的手机支付方式。通过 Stripe 接入时，客户在获批的 TWINT 应用中认证并批准付款，Stripe 会向商家通知支付成功或失败。它可以作为瑞士市场的本地钱包选项，但启用 TWINT 不只是打开 Dashboard 开关：商家网站需要符合明确的信息展示和业务审核要求，结账时还必须以瑞士法郎 CHF 展示价格。

本文梳理 Stripe TWINT 的商家资格、网站审核、客户流程、金额限制、退款及 Connect 适用范围。TWINT 的要求可能随商家国家和业务类别变化，最终以 Stripe Dashboard 当前能力状态和官方文档为准。

## 商家国家与客户市场

Stripe 当前文档列出多个欧洲国家的商家账户可以申请 TWINT，包括瑞士及其他受支持国家；客户使用国家为瑞士。商家可使用 Merchant 或 Connect 平台/Marketplace 账户，但业务模型仅支持 B2C，不支持 B2B。即使账户所在国家列在支持范围，商家仍可能需要完成合规审核才能启用。

TWINT 的客户结账展示币种为 CHF。若商家销售实体商品，Stripe 要求网站提供寄送至瑞士的选项；若只支持瑞士以外配送，即使支付方式已启用，也无法满足相应网站要求。结账之前应确认商品、运输范围和价格信息都与瑞士客户场景匹配。

## TWINT 审核对网站的要求

请求启用 TWINT 前，商家网站必须可正常访问，不能设置密码，也不能仅显示“即将上线”。Stripe 文档要求网站展示业务信息，包括法定商家名称、企业法律形式、完整业务地址、服务条款，以及至少一种联系方式，例如联系邮箱或电话号码。个体经营者还需展示经营者的姓名。

网站必须以客户当地货币展示价格；到 Checkout 阶段应显示 CHF。商家可以用 Stripe Adaptive Pricing 自动进行币种本地化，但需验证结账页面实际显示结果符合要求。不能只在网站底部写“支持瑞士”，而商品页和结账页仍只显示其他货币。

TWINT capability 可能在完成入驻核验前保持 pending。申请后应在 Dashboard 检查能力状态，必要时联系 Stripe 支持。若商家变更网站地址、条款、法定名称或业务模式，也应重新确认资料与审核要求仍符合条件。

## TWINT 支付流程

客户选择 TWINT 后，使用已批准的手机应用验证并授权付款。Stripe 提供即时支付结果通知，但订单系统仍要以后端 PaymentIntent、Checkout Session 和 webhook 的状态为准。用户关闭浏览器或没能返回商家页面时，服务端依然可能收到付款结果。

TWINT 适用于符合条件的 Stripe 产品和账户，支持 Connect。若平台通过 Connect 使用，应检查关联账户的资格、支付对象所属账户和资金对账上下文。不能只在平台主账户启用 TWINT，就假设所有关联商家都自动可用。

Stripe 当前文档列出的交易金额范围为最低 0.50 CHF、最高 5,000 CHF。商家还应在创建 PaymentIntent 或 Checkout Session 时检查币种、总额和支付方式限制。价格中若包含税费、折扣或运费，应以最终总额核对是否在限额内。

## 一次性订单、订阅与授权

TWINT 文档将其列为可重复使用的支付方式并支持经常性付款，但商家仍需依照 Stripe 当前集成完成客户授权和支付方式设置。首次付款成功不表示未来每次付款都保证成功；订阅要结合发票和订阅对象的实际状态更新客户权益。

如果订阅业务面向瑞士消费者，页面应清楚说明计费周期、价格和取消办法。对支付失败的订阅，要使用 Stripe 的失败付款处理和客户通知流程，而非重复创建订阅。客户更改套餐或付款授权时，也要确认新授权和发票状态符合业务政策。

## 退款和争议处理

TWINT 支持全额与部分退款，原付款完成后 180 天内可以发起退款。退款通常几分钟处理完成，但退款不可取消。TWINT 直接把退款返回客户的原始支付来源，可能是 TWINT 余额或关联付款方式，而不是通过冲正原交易完成。

多次部分退款累计不得超过原始支付金额。客服在提交后应记录 Refund 对象和状态，不要在请求刚提交时就向客户保证资金已经到账。若使用退款 API，需通过 Stripe 返回结果更新内部订单、财务对账和客户通知。

TWINT 支持全额争议，不支持部分争议。由于争议能力和证据流程会影响运营，商家应保留订单、履约、客户沟通和退款记录，收到 Stripe 事件后及时核实争议对象和金额。Connect 平台还要确认争议扣款属于平台账户还是关联账户。

## 常见启用问题

**能力一直处于 pending。** 核对 Stripe 对网站法定信息、CHF 价格、配送范围和账户资料的审核要求。

**客户看不到 TWINT。** 确认客户所在地、账户国家、币种、金额、产品模式和支付方式动态展示设置。

**商品页只显示其他货币。** TWINT 要求在结账前展示 CHF，检查 Adaptive Pricing 或多币种价格设置。

**业务只接受 B2B 订单。** Stripe 当前文档列明 TWINT 为 B2C 支持，B2B 不在可用业务模型中。

**支付成功页触发重复订单。** 通过服务端 webhook 和支付对象更新状态，避免依赖浏览器刷新。

**退款后订单显示已完成但金额不符。** 检查原始支付金额、累计部分退款和 Refund 状态，不能超过原交易金额。

## 上线审核清单

- Stripe 商家账户国家和 Connect 模式支持 TWINT；
- 业务面向 B2C，且商品类别通过限制检查；
- 商家网站公开可访问，不是密码保护或 Coming Soon；
- 展示法定名称、法律形式、完整地址、服务条款和联系渠道；
- 商品结账以 CHF 展示；
- 实体商品提供瑞士配送；
- Dashboard 中 TWINT capability 已从 pending 转为可用；
- 金额在 0.50 至 5,000 CHF 的当前限额范围；
- 测试应用授权、付款成功、失败和页面未返回；
- webhook 签名验证与幂等处理已配置；
- 退款和争议状态能同步到客服及财务系统。

## 总结

Stripe TWINT 为瑞士客户提供本地手机应用授权付款，使用 CHF，并可由符合资格的商家和 Connect 平台集成。启用前要满足 B2C、网站公开信息、法定商家资料、CHF 价格和瑞士配送等要求；能力状态在完成审核前可能保持 pending。

TWINT 支持全额与部分退款，退款窗口为 180 天，且退款不能取消；订单和退款状态应由 Stripe 服务端对象与 webhook 驱动。先完成账户资格、网站资料和端到端付款测试，再向瑞士消费者开放 TWINT。

## 参考资料

- [Stripe：TWINT 支付方式说明](https://docs.stripe.com/payments/twint)
- [Stripe：动态支付方式](https://docs.stripe.com/payments/payment-methods/dynamic-payment-methods)
- [Stripe：Checkout 价格本地化](https://docs.stripe.com/payments/currencies/localize-prices)
- [Stripe：退款 API](https://docs.stripe.com/api/refunds)
