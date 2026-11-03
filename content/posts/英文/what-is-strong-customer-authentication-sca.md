---
title: "What Is Strong Customer Authentication (SCA)?"
date: 2026-11-03
slug: "what-is-strong-customer-authentication-sca"
description: "Learn what Strong Customer Authentication means, how its authentication factors work, and when SCA requirements may apply to online payments in Europe."
tags:
  - "Strong Customer Authentication"
  - "SCA"
  - "PSD2"
  - "European payments"
  - "card authentication"
draft: false
categories:
  - "Payment Regulations"
---

If you make online card payments to businesses in Europe, you may sometimes be asked to approve a transaction through your banking app or enter an additional verification code.

This can be part of **Strong Customer Authentication (SCA)**, a regulatory security requirement associated with the European payment services framework.

SCA is designed to reduce unauthorized payments by requiring stronger verification in situations covered by the relevant rules.

It is particularly important for merchants accepting online payments in the European Economic Area (EEA), payment providers, card issuers, and customers using cards for cross-border transactions.

## What Does Strong Customer Authentication Mean?

Strong Customer Authentication is an authentication requirement under the European Union's revised Payment Services Directive, commonly known as PSD2, and its related regulatory technical standards.

Under the applicable framework, authentication generally needs to use at least two independent elements from different categories:

- **Knowledge:** Something the customer knows, such as a password or PIN.
- **Possession:** Something the customer possesses, such as a registered device or security token.
- **Inherence:** Something the customer is, such as a biometric characteristic.

The factors must meet the relevant independence and security requirements. Simply asking for two passwords does not automatically satisfy the concept of two-factor authentication under SCA.

## Examples of SCA in Online Payments

A bank may implement SCA using different combinations of authentication factors.

**Banking app approval**

A customer receives a transaction approval request in a registered banking app and confirms it using a device-based security method.

**Password and device verification**

The customer enters a password and completes a separate verification step linked to a registered device.

**Biometric authentication**

A customer uses fingerprint or facial recognition through a supported authentication process.

The exact method depends on the issuer and its implementation. Not every banking app uses the same combination of factors.

## When Does SCA Apply?

SCA generally applies to certain electronic payment transactions within the scope of the European regulatory framework.

For remote electronic payments, the rules include requirements for dynamically linking authentication to the amount and payee.

However, SCA is not a requirement to challenge every payment. The framework includes exemptions and exclusions for particular circumstances.

Examples may include certain low-value remote transactions, eligible recurring transactions after the initial setup, certain low-risk transactions processed under a transaction risk analysis exemption, some trusted-beneficiary arrangements, and other specifically defined situations under the applicable rules.

Whether an exemption can be used depends on the transaction, payment provider, issuer, and regulatory conditions. A merchant cannot assume that every transaction below a particular amount will be exempt.

## What Is the Difference Between SCA and 3-D Secure?

SCA and 3-D Secure are related, but they are not the same thing.

**SCA is a regulatory requirement.** It defines authentication standards that must be met for transactions within its scope.

**3-D Secure is a technical authentication protocol.** It provides a framework through which merchants, card networks, and issuers can exchange information and authenticate online card payments.

3-D Secure 2 is commonly used to support SCA for online card transactions, but the two concepts should not be treated as interchangeable.

SCA can also apply to payment situations beyond ordinary online card checkout, depending on the payment method and regulatory scope.

## What Happens If SCA Cannot Be Completed?

If a transaction requires SCA and the required authentication is not successfully completed, the payment may be declined or stopped.

Common problems include an unavailable registered phone or device, inability to access the issuer's authentication app, an expired verification code, an authentication timeout, or an unavailable issuer authentication service.

Customers should contact their card issuer when authentication repeatedly fails. Merchants should make sure their checkout correctly handles authentication outcomes and does not treat a failed authentication as a successful payment.

## Does SCA Apply to Every International Card Payment?

No.

A transaction involving a European merchant, a European cardholder, or a foreign merchant does not automatically produce the same SCA result in every situation.

The applicability depends on factors such as the payment service providers involved, transaction type, relevant jurisdiction, and regulatory scope.

A merchant accepting cards internationally should rely on its payment provider's compliance guidance rather than assuming that one authentication rule applies worldwide.

## How Does SCA Affect Virtual Cards?

Virtual cards are still card payment instruments. Using a virtual card does not automatically remove authentication requirements.

If a transaction is within the scope of SCA and requires authentication, the virtual card's issuer and payment infrastructure must support an appropriate authentication process.

Before using a virtual card for European online subscriptions or digital services, check whether the issuer supports the verification methods required by the merchant.

[CBPayments](https://www.cbpayments.cc/) offers virtual and physical card options for online payments. Cardholders should review the available features and confirm compatibility with the merchant and issuer requirements before relying on a card for recurring purchases.

## Frequently Asked Questions

**Is SCA the same as two-factor authentication?**

SCA generally requires two independent authentication elements from different categories. It is more specific than simply using two verification steps.

**Does SCA apply only to credit cards?**

No. The framework concerns payment services and relevant electronic transactions, not exclusively credit card payments.

**Can a recurring payment be exempt from SCA?**

Certain subsequent recurring transactions involving the same amount and payee may qualify for an exemption, subject to the applicable rules. The initial setup and later transactions may be treated differently.

**Does SCA guarantee that a payment is legitimate?**

No. SCA helps strengthen authentication, but it cannot eliminate all fraud or payment disputes.
