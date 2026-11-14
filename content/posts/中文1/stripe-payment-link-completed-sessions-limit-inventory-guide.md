---
title: "Stripe Payment Link 限量销售：完成次数上限、停用与库存履约"
date: 2026-11-14
description: "讲解 Stripe Payment Link 的 completed_sessions 限制、链接 active 状态、Checkout webhook 对账，以及避免限量商品超卖的应用侧库存设计。"
slug: "stripe-payment-link-completed-sessions-limit-inventory-guide"
tags: ["Stripe Payment Links", "Checkout", "库存", "限量销售", "Webhook"]
keywords: ["Stripe Payment Link 限量", "completed_sessions limit", "Stripe Payment Link 停用", "Stripe 限量销售库存", "checkout.session.completed"]
---

# Stripe Payment Link 限量销售：完成次数上限、停用与库存履约

商家常用 Stripe Payment Links 快速销售限量商品、活动名额或某个阶段的促销产品。Payment Link 对象支持基于已完成 Checkout Session 数量的限制，并提供 `active` 状态控制链接是否继续可访问。这个能力适合限制某条付款链接的累计完成次数，但它不是完整的库存仓储系统：它不会替商家处理不同商品 SKU 的库存锁定、发货、取消订单后释放库存或多渠道同步。[Payment Link 对象 API](https://docs.stripe.com/api/payment-link/object)。

要安全售卖限量商品，应将 Payment Link 的购买次数上限与自己的订单、库存和 webhook 履约流程一起设计。前端显示“剩余 5 件”并不能保证实际库存仍有 5 件；即使 Stripe 成功限制完成次数，也无法知道同一库存是否已在其他渠道售出。

## 理解 completed_sessions 限制

Payment Link 的 `restrictions.completed_sessions` 配置包含 `limit` 和当前 `count`。Limit 表示允许完成的 Checkout Session 数量上限；Count 记录当前已经完成并计入该限制的 Checkout Session 数。商家可以按营销活动或名额销售需要设置限制，并通过 API 或 Dashboard 查看对应 Payment Link 状态。

这里的计数单位是 Checkout Session，而不一定是一件商品。若客户能在一笔 Session 中购买多个数量，限制 20 个 Session 并不等于只卖出 20 件商品。若一个 Session 包含多个商品，单一的完成次数限制也无法替代按 SKU 或席位类型管理库存。设置限制前先确认 Payment Link 的商品、可调整数量、多商品组合和计数逻辑是否符合销售规则。

同时，创建 Checkout Session 与付款最终状态是不同阶段。对可能延迟确认的支付方式，应关注 `checkout.session.completed` 与 `checkout.session.async_payment_succeeded` 等实际事件，并按具体支付方式判断何时可以履约。不能把一个页面跳转或状态提示当成到账凭证。

## Payment Link 停用与访问行为

Payment Link 的 `active` 属性决定该链接 URL 是否继续可用。当 `active=false` 时，客户访问 URL 会看到链接已停用的提示。活动结束、库存售罄或促销价格停止后，可以停用不再使用的链接，避免客户继续进入旧结账页面。

停用旧链接不会自动修改已创建的 Checkout Session、已完成订单或已经启动的异步付款。活动结束时，需区分新客户是否还能开始结账、已有 Session 是否仍在有效期内，以及已付款订单如何履约。若一个限时活动的 Session 在关闭链接前已经创建，还应检查这些未完成订单如何处理，不能只通过 `active=false` 假设所有在途订单都立即消失。

若客户访问停用链接，应提供新的产品页或联系客服路径，说明活动已结束并推荐可用替代品。不要直接把旧链接重定向到另一个完全不同的产品，造成客户误以为仍在购买原商品。

## 限量销售的库存架构

如果商品只有一个销售入口且按订单数量售卖，可以在订单系统中建立库存台账，以订单行项目、支付状态和商品数量记录占用。对于多个 Payment Links、网站购物车、线下门店或市场平台共同销售的 SKU，库存必须由统一的服务端系统决定。Payment Link 的完成次数限制无法感知其他渠道的销量。

常见实现会在创建订单或支付流程时进行库存预留，在付款成功后将预留转为已售；超过有效时间仍未付款则释放预留。需要处理付款成功但 webhook 延迟的情况，避免同一件商品重新售给另一个客户。若业务使用 delayed payment method，需明确是启动付款时占用名额，还是最终成功后才占用，并接受相应的超卖或暂时锁库存风险。

如果希望通过固定售卖链接控制数量，可以让库存服务在订单生成前分配唯一名额或订单号。对于需要强一致的限量发售、按不同款式库存或抢购场景，建议由应用控制库存和支付 session 创建；不要仅依赖公开 Payment Link 的总 Session 限制。

## Webhook 与订单履约同步

服务器端订阅适用的 Checkout 与支付事件。收到事件后验证 webhook 签名、模式、账户上下文和事件 ID，再将事件写入持久化队列。后台 worker 关联 Payment Link、Checkout Session、客户和本地订单，确认付款是否成功、订单数量是否超出本地可售库存，再触发发货或开通服务。

一个 Payment Link 可以被很多客户共用，不能只根据 link ID 将付款归给某个固定用户。若 Link 售卖需要登录用户身份、定制内容或特殊权限，考虑将 Checkout Session 与服务端生成的订单关联，并验证客户返回的 Session 属于该用户。不要通过浏览器任意提交 Stripe URL 或 Session ID 来确定订单归属。

Webhook 可能重复或乱序到达。以 event ID 和 Session ID 做幂等，保证同一成功 Session 不会重复出库或发放名额。若业务在 `checkout.session.completed` 时先创建待验证订单，随后收到异步成功或失败事件，需按实际付款状态推进订单状态，不要将已失败的延迟付款仍标为可发货。

## 退款、取消和名额释放

客户取消订单或退款时，Stripe 退款状态与业务库存状态需要分别处理。若商品尚未发货且退款成功，业务可能释放库存；若已经履约、定制或消费，则需要根据退货政策决定是否重新入库。退款被发起但尚未成功时，不应提前把商品库存释放给下一个买家。

名额类商品也要定义释放规则。例如活动报名后退款，是否重新开放报名；订阅套餐的 Payment Link 限量是限制新建订阅数量，还是只限制一次性购买 Session？这些业务边界要在规则中明确。Stripe 的 completed_sessions 限制计数方式不替代业务侧的退款后库存重算；如果活动要重新开放名额，检查原 Payment Link 的当前状态与可用配置，再决定继续使用、更新或创建新链接。

客服和财务要使用同一订单状态定义。保留 Payment Link ID、Checkout Session ID、PaymentIntent/Subscription ID、Refund ID、库存预留 ID 和每次状态变更原因，方便售后、对账与防止重复处理。

## 测试方式与场景

在测试模式验证链接上限和完整支付流程。至少覆盖达到上限前、达到上限后、客户多次打开同一链接、关闭链接前已有 Session、异步支付成功/失败、重复 webhook、付款后取消、退款失败和本地库存不足等情况。使用不同测试客户和不同付款方式，确认具体事件顺序符合当前集成方式。

并发场景尤其需要验证：两个客户几乎同时启动结账时，本地库存服务如何分配名额；Payment Link 的 completed session limit 能否满足目标规则；超额时是否能阻止或补偿；如果 Stripe 已收款但本地已售罄，如何安全退款或人工处理。测试并发失败的恢复路径，而不仅仅是普通成功路径。

## 常见问题排查

**链接显示售罄但本地还有库存：**检查当前完成 Session 计数和 limit，确认限制按会话次数而非件数计算；检查之前的订单、测试数据与活动规则。

**本地库存卖完但 Payment Link 仍可购买：**说明订单库存与支付链接没有统一。及时停用或更新对应链接，并为已创建 Session 与已成功付款的客户建立补偿处理。

**链接停用后客户仍能完成付款：**检查客户是否在停用前已经进入 Checkout Session，查看 Session 与 PaymentIntent 当前状态。停用链接不应被视作撤销所有已开始或已完成付款。

**Session completed 但款项未到账：**区分 Checkout Session 状态和异步 PaymentIntent 状态，等待适用的支付结果事件或检索对象状态后再履约。

**重复出库：**检查 webhook event ID 与 Checkout Session 的幂等唯一约束，以及后台任务重试是否再次创建履约单。

## 上线检查清单

- `completed_sessions.limit` 与实际销售单位相符，区分 Session 数量和商品件数。
- 多渠道库存由统一服务端管理，Payment Link 限制不被误当成仓库库存。
- `active` 停用流程覆盖新结账、在途 Session 和客户替代入口。
- Checkout Session 与本地客户、订单及数量安全关联。
- 异步付款使用适用事件确认最终支付结果后再履约。
- Webhook 验签、幂等和乱序处理已经验证。
- 退款、订单取消、库存释放和再次销售规则一致。
- 测试了并发抢购、售罄、付款延迟和退款等异常路径。

## 总结

Stripe Payment Link 可通过完成 Checkout Session 数量限制控制链接级别的购买次数，并通过 `active` 属性停用旧链接。它适合作为营销和支付入口的控制，但无法替代按 SKU、订单、退款和多渠道设计的应用库存系统。结合本地库存预留、服务端 webhook 验款和幂等履约，才能让限量活动既方便下单，也能控制超卖风险。

Payment Link 的限制字段、Checkout 状态和各支付方式的事件行为可能因 API 版本与账户配置不同而变化。请以当前 Payment Link API、测试模式结果和实际业务规则为准。
