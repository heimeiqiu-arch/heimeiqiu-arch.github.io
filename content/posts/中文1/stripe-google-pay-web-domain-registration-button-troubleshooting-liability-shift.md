---
title: "Stripe Google Pay 网页接入：域名注册、按钮不显示与争议责任"
date: 2026-11-15
slug: "stripe-google-pay-web-domain-registration-button-troubleshooting-liability-shift"
description: "Stripe Google Pay 网页支付如何配置 HTTPS、注册根域和子域、排查按钮不显示，并理解 DPAN、FPAN、电子商务令牌与争议责任转移差异。"
keywords:
  - Stripe Google Pay 网页接入
  - Stripe Google Pay 域名注册
  - Google Pay 按钮不显示 Stripe
  - Stripe Google Pay liability shift
  - Stripe Payment Element Google Pay
tags:
  - 钱包支付

---

Google Pay 让客户使用 Google 账户中保存的银行卡在网站或应用完成付款。通过 Stripe 接入时，Checkout 通常可在启用支付方式后自动展示 Google Pay；Elements 集成则需要按对应的组件流程配置。网页接入还有一项容易漏掉的要求：所有展示 Google Pay 按钮的域名都需要注册，包括生产和测试域名、根域名及子域名。忘记注册 www 子域或预发布域，常会导致钱包按钮在某些环境中不出现。

Google Pay 也不意味着所有交易自动获得相同的争议责任转移保护。客户使用设备钱包令牌、浏览器或 Google 属性保存的卡、还是电商令牌，可能影响 SCA/3DS 和责任转移能力。本文梳理网页域名注册、组件选择、按钮排查、Connect 域名和令牌差异，帮助把支付体验和风险控制一并设计好。

## 支持范围与产品选择

Stripe 文档当前显示 Google Pay 支持多个账户地区的本地币种结算，客户位置除印度外覆盖广泛。它可用于 Checkout、Payment Links、Elements、Connect、订阅和发票等 Stripe 产品，并支持部分捕获、手动捕获、退款和争议处理。实际可用币种与账户国家有关，应以 Stripe 支持币种列表和 Dashboard 为准。

网页端可使用 Stripe Checkout 或 Elements。Checkout 中启用 Google Pay 通常不需要额外编写支付按钮逻辑；Elements 集成可以使用 Express Checkout Element 等适合的 UI。无论选哪种，先在 Dashboard 的 Payment Methods 设置中启用 Google Pay，再检查 Checkout Session 或 PaymentIntent 的服务端配置、币种、金额和客户设备条件。

Google Pay 网页集成必须通过 HTTPS 和通过 TLS 域名验证的证书提供服务。部分浏览器客户端还要求 Permissions-Policy 的 payment allowlist 包含当前页面和 Stripe 域名。若服务器策略头过严，Google Pay 组件可能被浏览器拦截。只在本地 HTTP 或不安全预览环境测试，不能代表生产站点配置正确。

## 注册全部网页域名

在 Stripe Dashboard 的 Payment Method Domains 页面注册每个会展示 Google Pay 按钮的域名。根域、www 子域、商店子域、独立 checkout 子域和预发布域都应逐一清点；测试和正式环境的域名也都要纳入。www.example.com 是单独的子域名，不能假设注册 example.com 后自动覆盖。

同一 Stripe 账户中，注册域通常只需一次；如有多个账户或环境，确认支付请求使用的密钥和账户上下文与域名注册所在账户一致。不要把 Secret Key 放入浏览器脚本；域名注册 API 应由受控的服务器端或 Dashboard 操作完成，并限制访问权限。

Connect 使用 direct charges 时，还要为每个使用 direct charge 的 connected account 配置对应网页域名。其他 charge type 通常不要求按同样方式为每个 connected account 单独配置，但仍要根据集成模式核对官方规则。测试平台账户域名已注册，并不意味着所有 direct charge 账户也能显示钱包按钮。

## 按钮不显示的排查顺序

先确认当前设备、浏览器和 Google Pay 钱包中是否具备可用卡片。Stripe 文档说明，若设备或集成条件不满足，Stripe 不会渲染 Google Pay 选项；测试时也需要满足钱包和 Stripe 测试卡的相应要求。使用 Stripe 的钱包测试页面和 Google 提供的测试套件，检查环境是否具备展示条件。

其次核对域名是否注册、HTTPS 证书是否有效，以及页面是否设置了合适的 Permissions-Policy。查看 Stripe Payment Method Domains 页面，逐个确认根域、www、移动站和子域状态。检查生产/测试账户是否误用错域名，或前端通过另一个 Stripe 账户的 Publishable Key 创建付款。

最后检查 Checkout 或 Elements 配置、Dashboard 支付方式开关、国家和币种是否适用，浏览器控制台是否有 wallet API、策略头或 iframe 错误。若使用支付方式动态选择，不要同时在服务端手动限制掉 Google Pay；若手动指定支付方式，确保配置包含正确的方式并适用于当前 Session 模式。

## DPAN、FPAN 与电商令牌的差别

Google Pay 交易可能使用不同类型的卡令牌。保存在 Google Pay 移动设备钱包中的卡通常使用 DPAN（设备主账号令牌）；保存在 Chrome 或 Google 服务中的卡可能使用 FPAN；在电商站点或应用中选择 Google Pay 的银行卡还可能作为 ecommerce token 处理。它们在支付流程和争议责任转移方面不完全一样。

Stripe 文档当前说明，Stripe 托管产品和 Stripe.js 的适用交易会自动处理部分责任转移；DPAN 可默认支持责任转移；FPAN 在使用 3D Secure 时能支持主要卡网络的责任转移；电商令牌当前不支持责任转移或 3DS。Visa 交易若不使用 Stripe 托管产品，在某些情形下还需在 Google Pay & Wallet Console 启用相应的 Fraud Liability Protection 设置。

因此，不要把“支付使用了 Google Pay”简单等同于“拒付责任已转移”。可在 Sigma charges 表中检查 card_token_type 等字段（如当前数据版本支持），并结合 Charge、PaymentIntent、3DS 结果和争议对象评估具体交易。对高风险订单，按适用的 Stripe Radar 规则和 3DS 策略处理。

## 付款状态、退款和争议

Google Pay 付款仍应按 Stripe PaymentIntent/Checkout Session 状态驱动履约。Webhook 验签、事件去重、订单 ID 关联和支付金额核对，与普通银行卡流程相同。不要只依赖钱包回调或前端 success 页面。Google Pay 支持全额和部分退款，具体退款处理按 Stripe 卡退款流程管理，并监听相应 Refund 状态事件。

客户仍可以对 Google Pay 交易提出争议，争议证据提交按照卡支付争议流程。收集订单、配送、客户沟通和服务交付证据，并按 Dashboard 或 Dispute 对象里的具体 due_by 提交。责任转移可能影响争议责任，但不代表所有争议一定自动判商户胜诉，也不替代按时提交证据。

## Android 应用与 Google Play 计费规则

Stripe Google Pay 支持应用内钱包付款，但 Google Play 对数字商品、内容和订阅的计费要求可能与实体商品、服务不同。Stripe 文档针对美国和欧洲经济区的数字商品应用列出若干第三方支付方式，但其他地区或商品类型的政策可能不同。上架 Android 应用前，查阅 Google Play 当前开发者政策和 Stripe 针对该地区的数字商品指南，确认适用的计费方式。支付集成的技术可行性不自动代表满足应用商店规则。

## 上线验证清单

在测试环境覆盖根域和全部子域、www、预发布域、HTTPS、Permissions-Policy、真实设备钱包、Chrome 钱包和受支持浏览器。测试 Checkout 与 Elements 两种集成，验证支付成功、失败、退款、争议 Webhook 和 Connect direct charge 的域名配置。检查实际 token 类型与 SCA/3DS/责任转移结果，确保客服和风险团队能够查看交易证据。

Google Pay 的稳定接入需要同时满足 Stripe 的钱包组件配置、浏览器安全策略和 Google 的域名注册要求。遇到按钮缺失时按域名、HTTPS、设备钱包和账户配置逐步排查；出现争议时根据实际令牌类型和认证结果分析，而不是假设所有钱包付款都享有同一责任转移。

## 官方资料

- [Stripe：Google Pay 网页接入](https://docs.stripe.com/google-pay?platform=web)
- [Stripe：Payment Method Domains](https://docs.stripe.com/payments/payment-methods/pmd-registration)
- [Stripe：Express Checkout Element](https://docs.stripe.com/elements/express-checkout-element)
- [Stripe：Google Pay 争议处理](https://docs.stripe.com/google-pay?platform=web#disputed-payments)
- [Google Play：开发者计费政策](https://support.google.com/googleplay/android-developer/answer/10281818)
