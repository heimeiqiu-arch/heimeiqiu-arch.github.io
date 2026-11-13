---
title: "What Is a 3-D Secure Exemption?"
date: 2026-11-03
slug: "what-is-a-3d-secure-exemption"
url: "/posts/英文/what-is-a-3d-secure-exemption/"
description: "Understand what a 3-D Secure exemption is, how low-value and transaction risk analysis exemptions work, and why an exemption does not guarantee that authentication will be skipped."
tags:
  - "3-D Secure exemption"
  - "SCA exemption"
  - "PSD2"
  - "online payment authentication"
  - "card payments"
draft: false
categories:
  - "Payment Regulations"
---

When a customer pays online, a merchant may initiate 3-D Secure authentication to help verify the cardholder.

However, not every payment needs to follow the same authentication path.

In certain circumstances, payment regulations allow an eligible transaction to be processed without the usual Strong Customer Authentication challenge. These situations are commonly referred to as **SCA exemptions**.

Exemptions can help reduce unnecessary checkout friction, but they are subject to specific conditions. They do not mean that merchants can simply disable authentication whenever they want.

## What Is a 3-D Secure Exemption?

A 3-D Secure exemption is a payment flow in which a transaction that might otherwise require Strong Customer Authentication is submitted under an applicable exemption.

In the European payment environment, exemptions are associated with the PSD2 regulatory framework and its related technical standards.

The merchant or its payment provider may request an eligible exemption as part of the payment process. The issuer may then decide whether to accept the exemption request or require authentication.

An exemption request is not the same as a guaranteed exemption.

## Common Types of SCA Exemptions

Several exemption categories are relevant to online card payments.

**1. Low-value transactions**

Certain remote electronic payments below the applicable regulatory threshold may qualify for a low-value exemption.

However, eligibility can depend on cumulative transaction values and the number of consecutive transactions since the last successful SCA. The threshold should not be interpreted as a blanket permission to skip authentication on every small purchase.

**2. Transaction Risk Analysis (TRA)**

A qualifying payment service provider may apply a transaction risk analysis exemption when the relevant fraud-rate and security conditions are satisfied.

The provider evaluates risk indicators and determines whether the transaction qualifies under the applicable rules.

This is not simply a merchant deciding that a customer looks trustworthy. The exemption is subject to regulatory conditions and provider-level controls.

**3. Trusted beneficiaries**

In certain circumstances, customers can add a payee to a trusted-beneficiary list maintained through the relevant payment service provider.

Subsequent eligible transactions involving that trusted beneficiary may qualify for an exemption.

The actual setup and availability depend on the issuer and payment arrangement.

**4. Secure corporate payment processes**

Certain payments made through qualifying secure corporate payment processes may fall within a specific exemption category.

The requirements are narrower than ordinary consumer card payments and should not be assumed to apply to every business card.

**5. Recurring transactions**

Subsequent transactions in a series of recurring payments involving the same amount and payee may be treated differently from the initial setup.

The first transaction may require SCA, while later eligible transactions may qualify for an exemption.

This distinction matters for subscription services and membership payments.

## How Does an Exemption Work During Checkout?

A simplified payment flow looks like this:

1. The customer enters card details.
2. The merchant or payment provider identifies whether an exemption may apply.
3. An exemption request is submitted through the appropriate payment flow.
4. The issuer evaluates the request.
5. The issuer may accept the exemption or require authentication.
6. The payment authorization proceeds according to the resulting payment flow.

The issuer's response is important. A merchant should not assume that a requested exemption has been accepted simply because it was included in the initial payment request.

## Exemption vs. Exclusion: What Is the Difference?

These terms are sometimes confused.

An **exemption** is a situation where a transaction within the relevant SCA framework may be processed without applying the usual authentication requirement, subject to the exemption conditions.

An **exclusion** refers to a transaction or payment situation that falls outside the scope of the relevant SCA requirement.

The legal treatment is different. A transaction that is excluded is not simply a transaction that has been granted an exemption.

Merchants should use their payment provider's classification and compliance guidance rather than treating the terms as interchangeable.

## Why Can an Exemption Request Still Lead to 3-D Secure?

There are several reasons:

- The issuer does not accept the requested exemption.
- The transaction does not meet the applicable conditions.
- The issuer's risk assessment indicates that authentication is necessary.
- The payment provider's configuration does not support the requested exemption.
- Regulatory or card-network rules require a different treatment.

This is why customers may still receive an authentication challenge even when the merchant expected a frictionless payment.

## Can Merchants Always Request an Exemption?

No.

Exemptions have eligibility requirements and may depend on the payment provider's capabilities, regulatory conditions, and issuer response.

Merchants should not repeatedly request exemptions simply to avoid authentication. Doing so can create additional declines, reduce payment reliability, or lead to compliance problems.

A better approach is to understand the payment provider's supported exemption types and monitor the outcomes of authentication and authorization together.

## What Should Customers Know?

Customers generally do not need to select an exemption manually.

If an issuer requires additional authentication, the customer should complete the verification through the official banking channel.

If a payment repeatedly fails, the customer should contact the card issuer or merchant rather than assuming the transaction was declined because of an exemption issue.

## Frequently Asked Questions

**Does a 3-D Secure exemption mean no authentication is needed?**

It may allow an eligible transaction to proceed without the usual SCA challenge, but the issuer can still require authentication.

**Can a merchant force an exemption?**

No. The merchant may request an eligible exemption, but the issuer and applicable payment rules determine the outcome.

**Are all small payments exempt from SCA?**

No. Low-value exemptions have conditions, including cumulative transaction and consecutive-payment limits.

**Does a virtual card automatically qualify for an exemption?**

No. The type of card does not automatically determine exemption eligibility. The transaction and payment arrangement must meet the relevant conditions.
