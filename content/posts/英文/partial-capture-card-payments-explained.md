---
title: "What Is a Partial Capture in Card Payments?"
date: 2026-10-17
draft: false
description: "Learn how partial capture works, why merchants capture less than the authorised amount, and what it means for your card balance."
categories: ["Payment Guides"]
tags: ["partial capture", "card authorization", "card payments", "payment processing"]
---

# What Is a Partial Capture in Card Payments?

Have you ever noticed that a merchant initially authorised one amount but later completed a transaction for a smaller amount? This can happen when the merchant uses a payment process known as **partial capture**.

Partial capture is used in certain payment environments when a merchant wants to complete a charge for less than the amount originally authorised. It is different from splitting a purchase into several separate payments, and it does not always produce the same result across payment providers.

Understanding the process can help customers interpret transaction records and available card balances.

## What Is Partial Capture?

A partial capture occurs when a merchant captures less than the amount that was authorised for a card transaction, where the payment setup and applicable rules permit it.

For example, imagine a merchant authorises £100 for an order. After preparing the order, the merchant determines that the final amount to charge is £85.

If the merchant's payment system supports partial capture, it may capture £85 rather than the full £100 authorisation.

The remaining £15 is not necessarily charged. The way the unused portion is released or handled depends on the payment system, authorisation arrangement, and merchant's processing rules.

This example is illustrative. Actual transaction handling varies by issuer, acquirer, card network, merchant integration, and jurisdiction.

## How Does Partial Capture Work?

A typical card payment may involve separate authorisation and capture stages.

### Step 1: The merchant requests authorisation

The merchant sends a request to check whether the card can support a payment for a specified amount. If approved, the issuer may reserve the amount against the card's available balance or credit.

An authorisation is not always the same as a completed charge.

### Step 2: The merchant confirms the final amount

The final amount may become clear only after the order is prepared or the service is delivered. For example, a merchant may remove an unavailable item or adjust an order before completion.

### Step 3: The merchant captures the payment

Where supported, the merchant submits a capture for an amount lower than the original authorisation.

### Step 4: The payment proceeds through later processing

The captured amount continues through the applicable clearing and settlement process. The unused authorised amount may be released, adjusted, or handled according to the relevant rules.

The timing of the balance update depends on the issuer and payment arrangement.

## Why Would a Merchant Use Partial Capture?

Partial capture can be useful in several situations.

**An item is unavailable.** A retailer may authorise the order value but ship only the items it has in stock.

**The final order total changes.** The merchant may need to adjust the amount after packing, weighing, or confirming the order.

**A service is completed in stages.** Some business payment arrangements allow an initial authorisation followed by a capture reflecting the amount due for a particular stage.

**The merchant's system separates authorisation from final charging.** Certain merchants do not finalise the exact amount until a later step in the fulfilment process.

Not every merchant or payment provider supports partial capture. Some require a different payment flow, a new authorisation, or another method of adjusting the transaction.

## Partial Capture vs Partial Authorisation

These terms sound similar but refer to different stages of payment processing.

| Term | Meaning |
|---|---|
| Partial authorisation | The issuer approves only part of the amount requested, where supported |
| Partial capture | The merchant captures less than the amount previously authorised, where supported |
| Split payment | A purchase is paid using multiple payment methods or transactions |
| Refund | The merchant returns money from a previously processed transaction |
| Reversal | An earlier transaction or authorisation is cancelled or reversed under the applicable process |

For example, if a merchant requests authorisation for £100 but the issuer approves only £60, that may be a partial authorisation. If £100 was authorised and the merchant later captures £85, that may be a partial capture.

The availability and handling of each process depend on the payment product and transaction type.

## Why Might the Original Authorised Amount Still Appear?

After a partial capture, a cardholder may temporarily see the original authorisation alongside the completed transaction, or may see an available balance that has not yet fully updated.

This can happen because authorisation records, captured transactions, and balance adjustments may be updated at different times.

For example:

- The original authorisation may still appear as pending.
- The captured amount may appear as a separate posted transaction.
- The unused portion may remain temporarily reflected in the available balance.
- The issuer's app may take time to display the final adjustment.

A pending authorisation is not necessarily an additional completed charge. To understand the status, check whether the transaction is pending or posted and review the available balance as well as the transaction history.

For more context, read our guide to [why card payments can remain pending](https://heimeiqiu-arch.github.io/posts/why-does-a-virtual-card-payment-stay-pending/).

## Does Partial Capture Mean You Will Be Charged Twice?

Not by itself. Partial capture describes how much of an earlier authorisation the merchant completes. It does not inherently mean that the merchant has charged the card twice.

However, payment records can be confusing when the original authorisation remains visible while the captured transaction appears separately.

To check what happened:

1. Compare the transaction dates and amounts.
2. Identify which entry is pending and which is posted.
3. Check whether the original authorisation has been released or adjusted.
4. Contact the merchant if the completed charge does not match the order.
5. Contact the card issuer if the transaction appears duplicated or the balance does not update within the expected timeframe.

If two separate posted charges remain for the same purchase, ask the merchant to investigate and contact the issuer if necessary.

## What Happens to the Unused Amount?

There is no single timeline that applies to every card payment.

The unused portion of an authorisation may be released or adjusted according to the payment arrangement. The timing can depend on whether the merchant sends an appropriate adjustment, the type of transaction, issuer processing, and the applicable card network rules.

A merchant's capture of a smaller amount does not guarantee that the remaining available balance will update immediately.

If the unused amount remains unavailable longer than the merchant or issuer's stated timeframe, contact the card issuer with the transaction date, amount, and status shown in your account.

## How Does Partial Capture Affect Virtual Cards?

A virtual card transaction may also involve separate authorisation and capture stages, depending on the card product and merchant setup.

If you use a virtual card for an online purchase, keep the following in mind:

- The authorised amount may temporarily affect your available balance.
- The final posted amount may differ from the original authorisation.
- A merchant may use a payment flow that does not support partial capture.
- Spending limits or issuer controls may affect later transaction attempts.
- The release of unused funds depends on the relevant provider's processing rules.

If you are choosing a card for international online purchases or subscriptions, review the card's transaction limits, supported payment types, fees, and provider terms. You can find more information about available card options at [CBPayments](https://www.cbpayments.cc/).

## What Should You Do If the Amount Looks Wrong?

Start by checking the order confirmation or invoice against the transaction shown in your card account.

If the merchant completed a lower charge than the original authorisation, determine whether the original entry is still pending. If the posted amount is incorrect, contact the merchant and request an explanation or correction.

If the balance remains affected by an old authorisation, ask the issuer whether the authorisation is still active and when the unused amount is expected to be released. Avoid assuming that every pending entry is a completed charge.

## Final Thoughts

Partial capture allows a merchant to complete a card transaction for less than the amount originally authorised, when the payment system supports it. It is useful when the final purchase amount changes, but the authorisation and capture stages can make transaction records temporarily confusing.

The key is to distinguish a pending authorisation from a posted charge, compare the final amount with the order, and contact the merchant or issuer if the records do not reconcile.
