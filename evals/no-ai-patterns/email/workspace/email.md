Subject: Incident Report — Webhook Delivery Disruption on March 3, 2026

Dear Valued Customer,

I hope this message finds you well. We're reaching out to provide a comprehensive update regarding the recent disruption to webhook deliveries that may have impacted your integration with Fernpost.

**What Happened**

On March 3, 2026, between 14:05 and 15:47 UTC, webhook deliveries from our platform experienced significant failures. During this window, our delivery workers were unable to establish secure connections to the message queue — the TLS certificate on the internal load balancer had expired. As a result, 312 webhook deliveries to your endpoints failed, and an additional 41 were delayed by more than 30 minutes.

**Impact on Your Account**

It's important to note that no data was lost. Every failed delivery was safely stored in our retry queue, ensuring full recoverability. Your API keys, account settings, and stored records were not affected in any way.

**Resolution**

Our engineering team swiftly identified the root cause and took immediate action:

- ✅ Replaced the expired certificate at 15:41 UTC
- ✅ Restarted the delivery workers at 15:47 UTC
- ✅ Replayed all 312 failed deliveries by 16:30 UTC

**Next Steps**

To prevent this from happening again, we're implementing several robust safeguards. Moving forward, certificates will be renewed automatically 30 days before expiry, and our monitoring will alert the on-call engineer 14 days before any certificate expires. Additionally, we are adding an end-to-end delivery check that runs every 5 minutes.

**Our Commitment to You**

We sincerely apologize for any inconvenience this may have caused. We understand how critical reliable webhook delivery is to your business, and we remain fully committed to providing the seamless, dependable service you deserve. Rest assured that we are taking every possible step to ensure this doesn't happen again.

If you have any questions or concerns, please don't hesitate to reach out to our support team. We're always here to help!

Warm regards,
The Fernpost Team
