---
title: "What Is a Card Security Code and How Is It Protected?"
date: 2026-11-03
slug: "what-is-a-card-security-code-and-how-is-it-protected"
url: "/posts/英文/what-is-a-card-security-code-and-how-is-it-protected/"
description: "Learn what a card security code is, how CVV and CVC values are used in online payments, and why merchants must protect this sensitive information."
tags: ["CVV", "CVC", "Card Security", "Online Payments"]
draft: false
categories: ["Payment Security"]
---

A card security code is a short numeric value printed on a payment card and used as an additional verification element in certain card-not-present transactions. Depending on the network, it may be called CVV, CVC, CID or another related name.

The code helps merchants and payment providers assess whether the person entering card details has access to information associated with the physical card. It is not a password and does not prove the identity of the person making a purchase. It is only one part of the broader payment verification process.

## Where to find the code

Many Visa and Mastercard cards use a three-digit code printed on the back, usually near the signature panel. American Express cards commonly use a four-digit code printed on the front.

Terminology varies. Visa commonly uses CVV2, Mastercard uses CVC2, and other networks may use different names. These values serve a broadly similar verification purpose.

## How it is used in an online payment

When a customer enters card details at checkout, the merchant may submit the card number, expiration date and security code to its payment processor. The processor and relevant payment participants handle the verification request according to their systems and rules.

The issuer may return a result indicating whether the code matched. A successful match does not guarantee approval: the issuer may still decline a transaction because of available funds, fraud controls, card restrictions or other factors. A mismatch does not always mean the card is stolen; the customer may have entered the code incorrectly.

## Why the code is sensitive

A security code can help an attacker complete certain online transactions if combined with other card information. Merchants must handle it carefully.

Payment card security standards impose strict restrictions on storing sensitive authentication data after authorisation. Card verification codes must not be retained after authorisation, even if encrypted.

Businesses should use payment integrations that handle card data securely and avoid recording security codes in application logs, customer support tickets or analytics systems.

## Does a security code prevent fraud?

No. It provides an additional verification signal, but it does not prevent every form of fraud. A code may be exposed through phishing, malware, compromised websites or other data theft. Some transactions may not require a code, depending on the merchant, transaction type, payment method and applicable rules.

Other verification methods, such as 3-D Secure authentication, may provide additional protection.

## What cardholders should never do

Do not send a card security code through ordinary email, public chat or an unsolicited message. Be cautious if someone claiming to represent a bank or payment provider asks you to disclose it. Contact the organisation through its official website or telephone number instead.

When entering card information online, check that the website is legitimate and the payment page is secure.

## What merchants should do

Minimise direct exposure to sensitive card data. Use a reputable processor or hosted payment page where appropriate. Restrict access to payment systems and ensure sensitive values are not written to logs.

Staff should receive training on payment data handling. Security reviews should include third-party scripts, checkout integrations and customer support workflows.

## Final thoughts

A card security code is an additional verification element for certain online payments, not a guarantee that a transaction is legitimate. Cardholders should protect it like other sensitive payment information. Merchants should follow payment security standards and ensure their systems do not retain prohibited authentication data.
