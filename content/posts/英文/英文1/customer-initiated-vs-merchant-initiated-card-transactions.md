---
title: "Customer-Initiated vs. Merchant-Initiated Card Transactions"
date: 2026-11-03
slug: "customer-initiated-vs-merchant-initiated-card-transactions"
description: "Learn the difference between customer-initiated and merchant-initiated card transactions, including examples, authentication, and how the two transaction types work together."
tags:
  - "customer-initiated transaction"
  - "merchant-initiated transaction"
  - "CIT"
  - "MIT"
  - "recurring payments"
draft: false
categories:
  - "Card Payment Processing"
---

A customer signs up for a subscription, enters card details, and approves the first payment. A month later, the service automatically charges the same card without asking the customer to return to the checkout page.

Why can the second payment happen without the same checkout process?

One important reason is the distinction between **Customer-Initiated Transactions (CITs)** and **Merchant-Initiated Transactions (MITs)**.

These terms describe who initiates a card transaction and are particularly important for subscriptions, stored payment credentials, and other payments made after the initial customer interaction.

## What Is a Customer-Initiated Transaction?

A Customer-Initiated Transaction is a payment initiated by the cardholder.

The customer actively participates in the payment process, usually by selecting a payment method and confirming a purchase.

Examples include buying a product from an online store, paying for a digital subscription during signup, making a one-time booking payment, paying an invoice through a hosted checkout page, or confirming an additional purchase in an application.

A CIT normally involves direct customer participation at the time the transaction is initiated.

Depending on the payment environment, the transaction may require 3-D Secure authentication or another verification method.

## What Is a Merchant-Initiated Transaction?

A Merchant-Initiated Transaction is initiated by a merchant using payment credentials previously stored with the appropriate customer agreement or authorization.

The customer does not actively submit the payment at that moment.

Common examples include monthly subscription renewals, eligible recurring membership payments, certain delayed charges, some payments triggered by an agreed service arrangement, and certain unscheduled payments made under a prior agreement.

An MIT is not simply any payment that happens automatically. The merchant must have an appropriate basis to initiate the transaction, and the payment must be correctly identified and processed.

## Key Differences Between CIT and MIT

| Feature | CIT | MIT |
|---|---|---|
| Who initiates the transaction? | Customer | Merchant |
| Customer action at payment time | Usually active | Usually not required |
| Common examples | Online checkout, manual purchase | Subscription renewal, eligible delayed charge |
| Stored credentials | May be used | Commonly used |
| Initial agreement | May be created during payment | Must be supported by an appropriate prior agreement |
| Authentication | Depends on applicable requirements | Depends on transaction type and applicable rules |

## How Do CIT and MIT Work Together?

Many recurring payment arrangements begin with a customer-initiated transaction.

**Step 1: Customer signs up**

The customer selects a subscription plan and enters card details.

**Step 2: Customer agrees to future charges**

The merchant explains the recurring billing arrangement and obtains the required agreement.

**Step 3: Initial transaction is processed**

The initial payment is submitted as a customer-initiated transaction. Applicable authentication may be performed.

**Step 4: Merchant stores the payment credential**

The merchant or its payment provider stores the card credential securely under the applicable stored-credential rules.

**Step 5: Future payments are initiated**

When the next billing date arrives, the merchant can submit an eligible merchant-initiated transaction using the stored credential and the appropriate transaction indicators.

This process helps distinguish a payment that the customer actively submits from one initiated under an earlier agreement.

## Are All Automatic Payments MITs?

Not necessarily.

The correct classification depends on the actual payment arrangement and applicable card-network rules.

For example, a customer may return to a merchant's website and manually click a payment button to renew a subscription. That transaction may be customer-initiated even though it relates to an existing subscription.

Likewise, some payments that happen without a fresh checkout action may have special classification requirements.

Merchants should not classify every payment as an MIT merely because the card number was stored previously.

## Why Does Correct Transaction Classification Matter?

Correct classification affects authentication, authorization, recurring billing, disputes, and payment reliability.

CITs and MITs may follow different authentication requirements. In some regulatory environments, eligible subsequent MITs can be treated differently from the initial customer-initiated transaction.

Issuers and payment networks use transaction indicators to understand the context of a payment. Clear records of the original customer agreement and subsequent transaction details can also help merchants respond to questions or disputes.

Incorrect indicators may cause processing problems or lead to additional authentication and declines.

## What Should Merchants Record?

A merchant operating a recurring payment model should maintain records that explain what the customer agreed to purchase, whether the payment is recurring or unscheduled, when the customer authorized the stored payment credential, the agreed billing amount or calculation method, the expected billing frequency, and how customers can cancel or change the agreement.

The merchant should also follow its payment provider's requirements for identifying the initial and subsequent transactions.

## Frequently Asked Questions

**Is a subscription renewal always an MIT?**

Not automatically. The classification depends on the agreement and how the payment is initiated.

**Does an MIT require the customer to enter an OTP every month?**

Not necessarily. Eligible MITs may be processed without a fresh interactive authentication challenge, but the applicable rules and payment arrangement determine the treatment.

**Can a merchant charge a card as an MIT without permission?**

No. Merchant-initiated payments require an appropriate customer agreement or authorization and must follow relevant rules.

**Can a customer manually pay a recurring invoice?**

Yes. A customer who actively submits a payment may be making a customer-initiated transaction, even if the payment relates to an existing subscription.
