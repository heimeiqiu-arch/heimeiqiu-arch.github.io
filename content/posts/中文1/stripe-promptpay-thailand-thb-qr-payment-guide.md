---
title: "Stripe PromptPay 接入指南：泰国 THB 二维码支付与发票限制"
date: 2026-11-15
slug: "stripe-promptpay-thailand-thb-qr-payment-guide"
description: "详解 Stripe PromptPay 的泰国商家与客户范围、THB QR 扫码流程、Checkout 与 Elements 限制、订阅发票模式和异步退款处理。"
keywords:
  - Stripe PromptPay
  - PromptPay Stripe 接入
  - 泰国 THB 支付
  - PromptPay 二维码
  - Stripe 泰国支付方式
tags:
  - Stripe
  - PromptPay
  - 泰国支付
  - 二维码支付
---

PromptPay 是泰国客户常用的实时支付方式。Stripe Checkout 可以向符合条件的泰国客户展示二维码，客户使用参与银行的应用扫描并授权付款。商家在 Stripe 确认交易后即可处理订单。对于在泰国经营的商家，PromptPay 能补充银行卡之外的本地支付选择；但它只使用泰铢 THB，不支持保存支付方式用于自动续费，也有不同产品集成限制。

接入之前，商家应先确认账户国家、客户所在地、产品模式和结账组件是否兼容。尤其要注意：Stripe 当前文档仅列出泰国 Stripe 账户可直接接受 PromptPay；美国商户的可用性属于 private preview，而不是所有账户都能启用。本文按 Stripe 官方资料介绍二维码流程、集成限制和退款状态管理。

## PromptPay 的支付体验

客户在结账页选择 PromptPay 后会看到二维码，再用泰国银行应用扫描并完成付款。客户主动确认支付，Stripe 会在付款完成后通知商家。商家可以根据业务选择 Stripe Checkout、Payment Links、部分 Elements 和其他支持的产品，但不同产品并非都支持所有界面模式。

二维码支付适合移动银行使用普遍、用户习惯扫二维码付款的场景。桌面客户可以在电脑页面显示二维码，再用手机银行扫描；手机客户需要考虑屏幕切换和二维码展示方式。订单页面应提示客户完成银行授权，并提供返回或刷新支付状态的路径。

与跳转钱包相比，PromptPay 的核心交互是展示二维码和等待银行确认。订单系统仍需设置待支付状态，等 Stripe 的服务端状态或 webhook 确认交易后再履约。不要仅凭客户截图、浏览器返回或用户点击“我已付款”就标记订单成功。

## 资格、币种与账户范围

Stripe 当前文档列出支持 PromptPay 的商家账户国家为泰国，客户所在地为泰国，展示币种为 THB。美国 Stripe 账户可用性仍是 private preview，需要申请并由 Stripe 审核，不能将预览访问当成普遍生产能力。

PromptPay 交易金额由支付方式及客户银行限制。Stripe 文档当前列出，泰国以外业务的默认单笔金额范围为 20 至 699,999 泰铢；结算货币最低额可能提高有效起付金额，客户也受其银行应用自身的付款上限约束。商家需要在创建 PaymentIntent 或 Checkout Session 前验证币种、金额和账户配置。

不同国家的 Stripe 账户与客户所在地之间的组合可能会变化，应以 Dashboard 支付方式设置为准。用户来到泰国网站或使用泰语浏览器，不代表商家的 Stripe 账户已经具备 PromptPay 能力。

## Checkout、Elements 与订阅限制

Stripe 文档列出 PromptPay 支持 Checkout、Payment Links、Connect、部分 Elements、Invoicing 和特定订阅发票场景，但有几个重要限制：

- Checkout 的订阅模式和 Setup 模式不支持 PromptPay；
- Express Checkout Element 不支持 PromptPay；
- 移动端 Payment Element 当前只支持 iOS 上的 PromptPay；
- Invoices 和 Subscriptions 只支持 send_invoice 收款方式；
- 订阅发票的 PromptPay 付款不会保存支付方式，也不会自动扣取未来账单。

因此，所谓“支持订阅”并不意味着能够建立自动续费授权。商家可以通过 send_invoice 为订阅账单提供 PromptPay 作为客户手动支付方式，但客户每期仍需完成付款流程。若业务需要自动扣费，应在页面中提供其他支持保存与重复扣款的支付方式，并明确告知客户。

如果集成使用动态支付方式，可以在 Dashboard 启用 PromptPay，让 Stripe 根据结账上下文决定是否展示。若手动列出支付方式，要按当前文档配置，并结合 Checkout 模式、Elements 平台和账户国家核实兼容性。

## 付款状态与履约

PromptPay 客户需要扫描二维码并在银行应用中确认。该确认可能与商家页面更新不同步。服务端应将 Session、PaymentIntent、内部订单号和金额建立关联，处理付款成功和失败事件，并实现 webhook 去重。

推荐的订单状态包括：创建中、等待客户扫码、付款处理中、已支付、已过期或取消。若客户扫描后没有及时返回网站，订单依旧应由 Stripe 事件更新。对于长时间未完成的付款，向客户展示如何返回结账或重新生成付款页面，不能重复创建多个已支付的相同订单。

使用 Connected Accounts 的平台还要确认事件账户上下文和资金责任。Connect 支持 PromptPay，但每个关联账户的资格、支付归属和对账方式仍应根据实际 Connect 模型进行配置。

## 退款通常需要等待最终结果

Stripe 文档说明 PromptPay 支持全额和部分退款，但退款流程取决于原始付款如何处理。通过托管跳转完成的支付使用异步退款；另一些银行账户退款流程可能需要客户提供银行账户信息。退款状态应以 Refund 对象和 Stripe 事件为准，商家不应在创建退款请求后立即把订单标记为已退款。

对于异步退款，监听 refund.updated 或 refund.failed 事件。退款成功时更新订单和财务记录；失败时 Stripe 会按对象状态返回结果，客服应依照适用流程另行处理。退款的处理时间与客户实际银行到账时间可能不同，沟通时要区分“Stripe 已成功提交”与“客户银行账上已可见”。

部分退款也需要保存累计退款金额，并确保多次退款不超过原始付款金额。财务对账应关联原始 PaymentIntent、退款对象和银行结算记录，避免把退款金额错误计为新的收费或重复退款。

## 常见接入误区

**以为所有国家的 Stripe 账户都能启用 PromptPay。** 当前官方支持国家和 preview 状态要在 Dashboard 与文档确认。

**把扫码完成等同于系统收款。** 订单仍要由 Stripe 服务端状态确认，客户端截图不能作为唯一依据。

**在订阅页宣传自动续费。** PromptPay 不保存支付方式；订阅发票模式需客户手动支付。

**忽略不同 Elements 的差别。** Express Checkout Element 不支持，移动端 Payment Element 有平台范围限制。

**用其他货币创建订单。** PromptPay 的展示币种为 THB，服务端应在创建会话前校验所有商品行。

**退款请求提交后就标记退款完成。** 异步退款需等待 Stripe 通知最终状态。

## 上线清单

- Stripe 账户符合 PromptPay 当前地区资格；
- 订单面向泰国客户并使用 THB；
- 交易金额符合当前最低和最高范围；
- 所选 UI 模式和设备受 PromptPay 支持；
- Checkout 未将 PromptPay 放入不支持的订阅或 Setup 模式；
- 手动支付方式列表或动态方式设置正确；
- 测试扫码成功、失败、未完成和返回延迟；
- webhook 验签、幂等与订单关联正常；
- 订阅采用 send_invoice 时向客户解释每期手动付款；
- 异步退款按 Refund 状态和 webhook 完成对账。

## 总结

Stripe PromptPay 为泰国客户提供银行应用扫码付款体验，使用 THB 并在付款后向商家提供确认。它适合一次性订单和客户主动付款场景，但不支持保存支付方式自动续费；Checkout 的订阅和 Setup 模式也不支持。发票和订阅账单通过 send_invoice 可提供手动付款路径，需让客户理解不是自动扣款。

接入前确认账户国家、设备、产品 UI、币种和金额，结账后依靠服务端事件确认付款。退款可能异步处理，应等 Stripe 最终退款状态再更新订单。美国账户的 PromptPay preview 访问应单独申请，不应默认视为已开放。

## 参考资料

- [Stripe：PromptPay 支付方式说明](https://docs.stripe.com/payments/promptpay)
- [Stripe：PromptPay 接入 API](https://docs.stripe.com/payments/promptpay/accept-a-payment)
- [Stripe：动态支付方式](https://docs.stripe.com/payments/payment-methods/dynamic-payment-methods)
- [Stripe：退款对象 API](https://docs.stripe.com/api/refunds/object)
