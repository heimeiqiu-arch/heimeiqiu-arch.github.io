---
title: "How to Reconcile Partial Card Captures"
date: 2026-11-04
slug: "reconcile-partial-card-captures"
url: "/posts/英文/reconcile-partial-card-captures/"
description: "Learn how partial card captures affect payment reconciliation and how to match authorization amounts, captured amounts, remaining balances, and refunds."
tags: ["Partial Capture", "Card Payments", "Payment Reconciliation", "Authorization"]
draft: false
categories: ["Payment Guides"]
---

A partial card capture happens when a merchant captures less than the amount originally authorized on a card. This may occur when an order is shipped in several parts, the final service amount is lower than the estimated amount, or only some items are ready for fulfillment.

Partial capture can make reconciliation more complicated because the authorization amount and the captured amount are not necessarily the same.

For example, a customer may authorize a payment of $200, but the merchant captures only $150. If the finance team compares the original authorization with the captured transaction, the $50 difference may look like a missing payment even though the transaction was processed as intended.

## Separate authorization from capture

An authorization confirms that a payment method can approve a transaction for a specified amount, subject to the issuer and payment network rules. It does not necessarily mean that the merchant has collected the full amount.

Capture is the step that requests the authorized funds. Depending on the provider and payment setup, a merchant may capture the full amount, capture part of it, or use multiple captures where supported.

For reconciliation, these events should be recorded separately. Do not treat the authorization amount as revenue or as a bank deposit.

## Build a transaction-level record

For each payment, retain the original authorization ID and amount, capture ID and captured amount, capture date and currency, order or invoice reference, any remaining authorized amount, refunds or reversals, and settlement batch and payout reference.

The exact fields available depend on the processor. If multiple captures are supported, each capture should be traceable to the original authorization and the relevant order.

## Example: one authorization, two captures

Suppose a customer places an order for $200. The merchant authorizes $200 but ships the order in two separate packages. The first capture is $120 and the second capture is $80.

The reconciliation record should show one authorization of $200 and two captures totaling $200. The captured total is not $400 simply because the authorization and capture events are both present in the report.

If only $120 is eventually captured, the remaining $80 should not be recorded as collected revenue. The business should check whether the remaining authorization was released, expired, or otherwise handled according to the provider's process.

## How to investigate a mismatch

Start by checking whether the report contains both authorization and capture events. If it does, group them by their shared payment or authorization reference.

Calculate the total captured amount. Compare that total with the order or invoice amount, while separately accounting for refunds and adjustments.

Next, inspect the settlement report. Only captured transactions that are eligible for settlement should normally be expected to contribute to the payout. The bank deposit may also be reduced by fees, refunds, or other adjustments.

If the captured amount differs from the expected amount, review the merchant's order history and the processor's event records. Do not assume that an incomplete capture is a technical error; it may reflect a deliberate fulfillment decision.

## Common mistakes to avoid

One mistake is counting authorization and capture as two separate sales. Another is treating the unused authorization amount as a refund. An authorization release and a refund are different events and should be recorded according to the processor's actual transaction data.

A further mistake is matching each capture independently to the full order value. When several captures belong to one order, reconcile their combined amount against the order total.

## Create a clear accounting policy

Decide how the business records authorizations, captures, refunds, and settlement entries. Apply the same policy across payment channels and document exceptions.

Businesses that use card payments for online services and operating expenses should also keep actual transaction and statement records. CBPayments offers card-based payment options, but the accounting treatment should always follow the transaction events shown by the relevant provider.

Partial captures are easier to reconcile when every event has a clear relationship to the original authorization, order, and settlement batch.
