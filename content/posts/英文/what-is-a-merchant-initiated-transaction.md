---
title: "What Is a Merchant-Initiated Transaction (MIT)?"
date: 2026-10-19
slug: "what-is-a-merchant-initiated-transaction"
description: "Understand merchant-initiated transactions, how they differ from customer-initiated payments, and why subscriptions and stored-card payments use them."
tags:
  - merchant initiated transaction
  - MIT
  - recurring payments
  - subscription billing
draft: false
---

# What Is a Merchant-Initiated Transaction (MIT)?

A subscription renews automatically, a cloud service charges for usage, or a hotel processes a later payment using card details provided earlier. In these situations, the customer may not be actively entering card details at the moment the charge occurs.

Some of these payments are processed as merchant-initiated transactions, commonly abbreviated as MITs.

Understanding MITs helps explain how recurring billing works, why a stored card may be charged without a new checkout session, and why an automatic payment can sometimes fail even when the card worked for the original purchase.

## What Is a Merchant-Initiated Transaction?

A merchant-initiated transaction is a card transaction initiated by a merchant under an applicable arrangement established with the customer.

The customer has generally provided the card details and agreed to the relevant payment terms earlier. The merchant then initiates a later transaction in accordance with that agreement and the applicable card-network rules.

An MIT is not permission for a merchant to charge a card whenever it wants. The merchant must have a valid basis for the transaction, follow the agreed terms, and comply with relevant payment requirements.

The exact classification and processing rules depend on the card network, payment provider, transaction type, and applicable regional requirements.

## How Is an MIT Different from a Customer-Initiated Transaction?

A customer-initiated transaction, or CIT, generally occurs when the customer actively participates in initiating a payment—for example, by entering card details at checkout or confirming a purchase through a supported payment flow.

An MIT is initiated by the merchant under a previously established arrangement, such as an eligible subscription renewal.

| Feature | Customer-initiated transaction (CIT) | Merchant-initiated transaction (MIT) |
| --- | --- | --- |
| Who initiates the payment? | The customer actively initiates it | The merchant initiates it under an established arrangement |
| Common example | Buying an item at checkout | Charging an eligible subscription renewal |
| Customer action at that moment | Usually participates directly | May not be actively present |
| Requirements | Depends on the payment and authentication flow | Depends on the original agreement and applicable MIT rules |

These categories are not interchangeable labels that merchants can choose arbitrarily. Correct transaction classification matters for authorization, authentication, and processing.

## Where Are Merchant-Initiated Transactions Used?

### Subscription Renewals

A streaming service, software platform, or online membership may charge a saved payment method each billing period. If the transaction meets the relevant requirements, the renewal may be processed as an MIT.

The original enrollment and subsequent billing must follow the applicable terms, including the agreed amount or pricing method and billing frequency.

### Usage-Based Billing

Some services charge based on measured usage. For example, a cloud service might calculate a bill after a usage period ends.

The merchant's ability to initiate that charge depends on the customer's agreement, the service's billing model, and the payment rules applicable to the transaction.

### Delayed or Unscheduled Payments

Certain industries may process later charges after an initial interaction, such as eligible additional charges related to a booking or service. These payments have specific requirements and should not be assumed to qualify as MITs merely because the customer is no longer present.

### Stored-Card Purchases

Merchants may retain payment credentials through a supported payment provider for future eligible transactions. The merchant must follow the relevant stored-credential and transaction-classification rules when using them.

## Does an MIT Require 3D Secure Every Time?

Not necessarily. Authentication requirements depend on the original transaction, the payment flow, the applicable regulations, the issuer, and the card-network rules.

A customer may be asked to authenticate when initially setting up a subscription or saving a card. Later eligible merchant-initiated payments may follow a different process.

However, merchants should not assume that every future charge will be exempt from authentication or guaranteed approval. Some transactions may require additional checks, and some issuers may decline a payment even when the original setup was successful.

Businesses should follow their payment provider's guidance on identifying and submitting CITs and MITs correctly.

## Why Can an Automatic Subscription Payment Fail?

A merchant-initiated payment can fail for many reasons, including:

- The card has expired or been replaced.
- The available balance is insufficient.
- The issuer blocks the transaction under its risk controls.
- The merchant's stored payment credential is no longer valid.
- The merchant submits an incorrect transaction type or credential data.
- The card does not support the merchant, transaction type, or currency.
- Additional authentication or customer action is required.

A successful initial payment does not guarantee that future renewals will succeed. Each later transaction is still subject to the card's current status and the issuer's authorization decision.

## What Can Customers Do If a Recurring Charge Fails?

If a subscription renewal fails, start with the merchant's billing page and the message associated with the failed payment.

1. **Check the card status.** Confirm that the card is active and that its details have not changed.
2. **Review the available balance.** Make sure sufficient funds or credit are available for the amount and any applicable currency conversion.
3. **Check merchant compatibility.** Some cards restrict recurring, cross-border, or particular merchant-category transactions.
4. **Follow any verification request.** If the provider asks you to confirm payment details or complete authentication, use its official website or app.
5. **Contact the issuer if needed.** The issuer may be able to explain a decline, although it may not disclose every fraud-control detail.

Avoid repeatedly retrying a failed payment without understanding the cause, as repeated attempts may lead to further declines or temporary restrictions.

## What Should Businesses Know About MITs?

Businesses that use recurring billing should clearly explain the payment arrangement before collecting a customer's card details.

Important practices include:

- Communicating the billing amount or calculation method
- Disclosing the billing frequency and renewal terms
- Keeping records of the customer's agreement
- Using a payment provider that supports the required transaction flows
- Correctly distinguishing customer-initiated and merchant-initiated transactions
- Providing a practical way to manage or cancel eligible subscriptions
- Handling failed payments and customer disputes appropriately

Clear billing communication can reduce confusion and help customers recognize legitimate recurring charges.

Businesses should also avoid treating a saved card as unlimited authorization. A stored credential does not remove the need to follow the original agreement and applicable rules.

## Can a Virtual Card Be Used for MITs?

Possibly. Some virtual cards support eligible recurring payments, while others may have restrictions related to merchant types, card lifecycle, balance, or transaction settings.

Before using a virtual card for a subscription, check whether the card supports recurring transactions and whether the merchant accepts that card type. You should also understand what happens if the card is replaced, paused, or has insufficient available funds at renewal time.

For users exploring cards for online services and overseas subscriptions, [CBPayments](https://www.cbpayments.cc/) provides information about available card solutions. Confirm the terms and recurring-payment support of the specific product before relying on it for ongoing billing.

## Final Thoughts

Merchant-initiated transactions allow eligible merchants to process payments under an arrangement established with a customer, making subscription renewals and certain later charges possible.

They are distinct from customer-initiated checkout payments and must be classified correctly. Customers should understand their billing agreements, while businesses should maintain clear consent records and follow the applicable processing rules.

If an automatic payment fails, check the card status, merchant restrictions, and issuer response before assuming the subscription or card itself is permanently unusable.
