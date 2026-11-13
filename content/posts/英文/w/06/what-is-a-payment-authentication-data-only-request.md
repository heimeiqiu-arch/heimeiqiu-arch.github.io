---
title: "What Is a Payment Authentication Data-Only Request?"
date: 2026-11-03
slug: "what-is-a-payment-authentication-data-only-request"
url: "/posts/英文/what-is-a-payment-authentication-data-only-request/"
description: "Learn what a data-only request means in 3-D Secure payment authentication, how it differs from a challenge, and why it does not guarantee cardholder authentication or payment approval."
tags:
  - "data-only authentication"
  - "3-D Secure"
  - "3DS2"
  - "payment authentication"
  - "card security"
draft: false
categories:
  - "Card Security"
---

Not every payment security process needs to display a verification screen to the customer.

In some 3-D Secure implementations, transaction information can be exchanged to support risk assessment without requesting an interactive cardholder challenge.

This type of flow is commonly described as a **data-only request**.

It is useful to understand the distinction because data-only processing is not the same as a successful cardholder authentication, and it does not automatically approve a payment.

## What Is a Data-Only Request?

A data-only request is an authentication-related flow in which transaction information is shared through the relevant 3-D Secure infrastructure without requesting an interactive cardholder challenge.

The purpose is to provide contextual information that may help payment participants evaluate a transaction.

Depending on the implementation, this information can include transaction amount and currency, merchant information, device and browser context, payment method information, and other supported transaction data.

The exact data elements depend on the 3-D Secure version, provider integration, and applicable specifications.

## How Does a Data-Only Flow Work?

A simplified process looks like this:

**1. Customer begins checkout**

The customer enters card details and submits the payment.

**2. Merchant prepares authentication-related data**

The merchant's payment integration collects the available transaction information.

**3. Data is transmitted through the supported infrastructure**

The relevant 3-D Secure components exchange the information according to the implementation.

**4. Payment participants use the available context**

The information may support risk analysis or other payment-security processes.

**5. The payment follows its applicable authorization flow**

The merchant or payment provider continues processing according to the returned results and payment configuration.

A data-only request should not be interpreted as a normal challenge flow that has been successfully completed.

## Data-Only vs. Frictionless Authentication

These terms can sound similar because neither necessarily requires the customer to enter a code or approve a notification.

However, they are not interchangeable.

**Frictionless authentication** is an authentication outcome in which the issuer determines that the cardholder can be authenticated without an interactive challenge.

**Data-only processing** involves sharing authentication-related information without performing the same interactive cardholder authentication process.

The distinction matters because the resulting status and liability treatment can be different.

Merchants should follow their provider's documentation rather than assuming that a data-only result is equivalent to an authenticated transaction.

## Data-Only vs. Challenge Authentication

A challenge flow asks the customer to complete an additional verification step.

For example, the customer may receive a banking app notification or enter a one-time password.

A data-only flow does not require that interactive step as part of the data-only request itself.

The two approaches therefore serve different purposes:

- Data-only: provide transaction information.
- Challenge: request additional cardholder verification.
- Frictionless: complete authentication without a visible challenge.

A payment implementation may support more than one type of authentication-related flow, but the applicable result depends on the protocol and provider configuration.

## Does a Data-Only Request Guarantee Payment Approval?

No.

There are several separate decisions in a card payment:

1. Whether authentication is performed.
2. Whether the issuer approves the authorization request.
3. Whether the transaction is later captured and settled successfully.

A data-only request does not guarantee any of these outcomes.

The issuer may still decline the payment because of insufficient funds, card restrictions, risk controls, or other authorization reasons.

## Does Data-Only Processing Provide 3-D Secure Liability Protection?

Merchants should not assume that it does.

Liability treatment depends on the relevant authentication result, card-network rules, transaction conditions, and other requirements.

A data-only request should not automatically be treated as equivalent to a fully authenticated 3-D Secure transaction.

Merchants should ask their payment provider how data-only results are represented, what they mean for the authorization flow, and whether any specific liability treatment applies.

## Why Would a Merchant Use Data-Only Processing?

A merchant may use data-only processing when its payment provider supports it as part of a broader risk or authentication strategy.

Potential purposes include supplying additional transaction context, supporting risk assessment, improving visibility into transaction characteristics, and integrating security data into a broader payment flow.

The availability and benefits depend on the specific implementation. Data-only processing is not a universal replacement for 3-D Secure authentication.

## What Should Merchants Check Before Using It?

Merchants should confirm several details with their payment provider:

- Which 3-D Secure versions and flows are supported.
- What data is collected and transmitted.
- How the resulting status is represented.
- Whether additional authentication can still be requested.
- How the flow interacts with authorization.
- What liability and compliance treatment applies.
- Whether the implementation is supported for the target card networks and regions.

Clear documentation is particularly important because different providers may use similar terminology for different technical processes.

## What Should Cardholders Know?

Most customers will not need to make a separate decision about data-only processing.

If a merchant uses this type of flow, the customer may simply complete checkout without seeing an authentication challenge.

However, the absence of a visible verification screen does not mean the transaction has been fully authenticated or approved.

Customers should still monitor their payment status and contact the card issuer if an unfamiliar transaction appears.

## Frequently Asked Questions

**Does data-only authentication mean the cardholder has been verified?**

Not necessarily. A data-only request shares transaction information but should not be confused with a completed interactive or frictionless cardholder authentication result.

**Can a data-only request be followed by a payment decline?**

Yes. The issuer can still decline the authorization request.

**Is data-only the same as frictionless 3-D Secure?**

No. Frictionless is an authentication outcome. Data-only is a distinct information-sharing flow.

**Does data-only automatically provide liability shift?**

No. Merchants must confirm the applicable treatment with their payment provider and the relevant card-network rules.
