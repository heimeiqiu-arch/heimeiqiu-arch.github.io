---
title: "What Is an Initial Stored Credential Transaction?"
date: 2026-11-03
slug: "what-is-an-initial-stored-credential-transaction"
url: "/posts/英文/what-is-an-initial-stored-credential-transaction/"
description: "Learn what an initial stored credential transaction is, how merchants obtain permission to save card details, and why the first payment matters for future transactions."
tags:
  - "stored credentials"
  - "initial transaction"
  - "card-on-file"
  - "CIT"
  - "recurring payments"
draft: false
categories:
  - "Card Payment Processing"
---

When you sign up for a subscription, a merchant may ask you to enter your card details once and allow future payments to be collected automatically.

The first transaction in this arrangement is important because it establishes the relationship between the customer's payment credential and the merchant's future billing activity.

This is commonly referred to as an **initial stored credential transaction**.

It helps payment providers identify when a card credential is first stored for future use and whether the customer actively participated in setting up the arrangement.

## What Is a Stored Credential?

A stored credential is a payment credential that a merchant or its payment provider retains for use in future transactions.

For card payments, this may involve a card number or a network token, depending on the payment infrastructure.

Stored credentials are commonly used for subscription renewals, membership payments, repeat purchases, one-click checkout, eligible delayed or unscheduled charges, and other payment arrangements where customers authorize future use.

Storing a payment credential does not give a merchant unlimited permission to charge the card. The future use must be consistent with the customer's agreement and applicable rules.

## What Makes an Initial Stored Credential Transaction Different?

An initial stored credential transaction establishes the first payment relationship in which the card credential is stored for future transactions.

The customer typically participates directly by entering the card information and agreeing to the merchant's payment arrangement.

Depending on the payment flow, the first transaction may be processed as a customer-initiated transaction and may require authentication.

The payment provider can also use the relevant stored-credential indicators to identify that the credential is being stored for future use.

## How Does the Process Work?

**1. The customer chooses a service**

For example, a customer signs up for a monthly software subscription.

**2. The merchant explains the payment arrangement**

The merchant should clearly communicate the price, billing frequency, renewal conditions, and cancellation process.

**3. The customer provides payment details**

The customer enters card information or selects an available payment method.

**4. The initial transaction is processed**

The payment is submitted through the merchant's payment provider with the appropriate stored-credential information.

**5. The credential is stored securely**

The merchant or its payment provider retains the credential in accordance with security and card-network requirements.

**6. Future transactions use the established arrangement**

Eligible subsequent transactions can reference the original stored-credential relationship.

## Does the Initial Transaction Always Need a Payment?

Not necessarily in every payment setup.

Some payment arrangements involve an initial account verification or credential-storage process rather than an immediate purchase. A zero-value account verification may be used where supported.

However, the merchant must follow the payment provider's and card-network's requirements for the specific transaction type. A verification request should not be treated as a successful purchase or as automatic permission for unlimited future charges.

## Does the Customer Need to Complete 3-D Secure?

The authentication requirement depends on the transaction, applicable regulation, issuer policy, and payment flow.

For example, an initial customer-initiated transaction within the scope of European SCA may require authentication unless a valid exemption or other permitted treatment applies.

Other regions and payment environments may use different requirements.

Merchants should not assume that every stored-credential setup requires the same verification process.

## What Information Should Be Disclosed to Customers?

Before storing a card for future use, a merchant should clearly explain the purpose of storing the card, whether payments will be recurring or occasional, the billing amount or how it will be calculated, the billing frequency or triggering conditions, how customers can cancel the arrangement, and how payment details can be updated.

Clear communication can reduce unexpected charges and disputes.

## What Happens If the Initial Transaction Fails?

If the initial payment or verification process fails, the merchant may not be able to establish the intended stored-credential arrangement.

Possible reasons include incorrect card information, insufficient funds, issuer restrictions, authentication failure, unsupported stored-credential processing, or payment-provider configuration problems.

Customers should verify the card details and authentication status before retrying. Merchants should avoid treating an incomplete initial transaction as a fully established recurring payment agreement.

## Why Is the Initial Transaction Important?

The initial transaction provides the reference point for later stored-credential activity.

It helps establish the context in which future transactions are submitted and supports correct identification of subsequent customer-initiated or merchant-initiated payments.

Without the proper initial setup, later charges may be incorrectly classified or rejected.

For customers who use virtual cards for online services, it is useful to understand whether the card can support both the initial payment and the later stored-credential transactions.

[CBPayments](https://www.cbpayments.cc/) offers virtual and physical card options for online payments. Before using a card for a subscription, check its support for the merchant's payment and authentication requirements.

## Frequently Asked Questions

**Is an initial stored credential transaction the same as a subscription payment?**

Not exactly. It is a transaction associated with establishing a stored payment credential. A subscription may be one reason for setting it up.

**Can the first stored-credential transaction be zero-value?**

Some payment systems support account verification without a purchase amount. Availability and processing requirements depend on the provider and card network.

**Does saving a card mean the merchant can charge it whenever it wants?**

No. Future charges must be supported by the customer's agreement and applicable payment rules.

**Can the cardholder remove a stored credential?**

Customers can generally request that a merchant remove saved payment details or cancel the relevant billing arrangement. The exact process depends on the merchant and payment provider.
