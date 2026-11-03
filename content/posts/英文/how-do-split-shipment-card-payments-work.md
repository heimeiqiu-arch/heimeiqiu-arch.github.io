---
title: "How Do Split-Shipment Card Payments Work?"
date: 2026-11-03
slug: "how-do-split-shipment-card-payments-work"
description: "Learn how card payments work when an online order is shipped in multiple packages, including authorization, separate shipment charges, and payment reconciliation."
tags:
  - "split shipment payments"
  - "partial presentment"
  - "card authorization"
  - "ecommerce payments"
  - "order fulfilment"
draft: false
categories:
  - "Card Payments"
---

# How Do Split-Shipment Card Payments Work?

An online customer orders five products, but only three are available for immediate dispatch.

The merchant ships the available products first and sends the remaining items later.

This creates a payment-processing challenge: should the customer be charged once for the entire order, or should each shipment be processed separately?

The answer depends on the merchant's checkout design, authorization strategy, card-network rules, and acquiring setup.

## What Is a Split-Shipment Payment?

A split-shipment payment occurs when one customer order is fulfilled through multiple shipments rather than a single delivery.

The merchant may need to process separate payment amounts as individual shipments are dispatched.

This is different from split tender, where a customer uses multiple payment methods to pay for one purchase.

## How Does the Process Work?

A simplified example:

A customer places an order worth $300.

- Shipment 1 contains goods worth $100.
- Shipment 2 contains goods worth $120.
- Shipment 3 contains goods worth $80.

The merchant may obtain authorization for the overall order amount, then submit separate clearing or presentment transactions as the shipments are fulfilled, where the relevant framework permits this approach.

Alternatively, the merchant may use separate authorizations for each shipment.

The appropriate approach depends on the payment network, transaction indicators, and processor capabilities.

## Why Might a Merchant Use One Authorization?

Obtaining authorization for the full order amount at checkout can reduce the need to ask the customer to repeat the payment process for each shipment.

However, the authorization has a limited validity period.

If the remaining goods are not shipped within the applicable period, the merchant may need to use a permitted reauthorization process or another supported payment arrangement.

## Why Might a Merchant Use Separate Authorizations?

Separate authorizations can align payment approval more closely with individual shipments.

However, this may create additional payment events and requires accurate order-level reconciliation.

The merchant must also ensure that the customer understands the payment arrangement and that the processing method complies with applicable rules.

## Split Shipment vs. Split Tender

These terms describe different situations.

**Split shipment** means one order is delivered in multiple packages or fulfilment stages.

**Split tender** means one purchase is paid using more than one payment method.

A customer may use split tender for a single shipment, while a merchant may process a split-shipment order using one card and multiple fulfilment events.

## What Happens When a Shipment Is Cancelled?

If part of an order is cancelled, the merchant should update its fulfilment and payment records.

The final amount collected should reflect the goods or services actually supplied and the applicable agreement.

Depending on the original authorization and capture structure, the merchant may need to adjust the transaction, release unused authorization amounts, or process a refund.

The correct treatment depends on the payment framework.

## Common Processing Problems

### Authorization Expires Before Later Shipments

A long fulfilment delay can cause the original authorization to expire.

### Duplicate Charges

Poor coordination between order management and payment systems can cause the same shipment amount to be submitted twice.

### Incorrect Shipment Amounts

The payment records may not match the actual value of the goods dispatched.

### Reconciliation Gaps

Separate shipment transactions must be linked to the original order so finance teams can understand the total amount collected.

## Best Practices for Merchants

Use a consistent order reference across payment and fulfilment systems.

Record each shipment's value, dispatch date, capture status, and payment reference.

Monitor authorization validity and use only the reauthorization or presentment methods permitted by the relevant provider.

Make the expected billing arrangement clear to customers, especially when multiple charges may appear.

## Frequently Asked Questions

### Does split shipment mean the customer will always see multiple charges?

No. The payment structure depends on the merchant's processing setup and applicable rules.

### Can a merchant capture the full order amount before shipping everything?

The answer depends on the merchant agreement, network rules, applicable law, and transaction type. Merchants should not assume that every order can be captured in full before fulfilment.

### Is split shipment the same as partial capture?

No. Split shipment concerns fulfilment in multiple deliveries. Partial capture concerns collecting less than the previously authorized amount.

Split-shipment payment processing requires close coordination between order management, fulfilment, and payment systems. Accurate references and clear customer communication help prevent duplicate charges and reconciliation errors.

For information about online card services, visit [CBPayments](https://www.cbpayments.cc/).

---
