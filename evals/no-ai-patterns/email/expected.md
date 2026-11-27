Subject: Failed webhook deliveries on 3 March 2026

Hello,

On 3 March 2026 between 14:05 and 15:47 UTC, 312 webhook deliveries to your endpoints failed and 41 more arrived over 30 minutes late. The TLS certificate on our internal load balancer had expired, so our delivery workers couldn't connect to the message queue. We replayed all 312 failed deliveries by 16:30 UTC, and since every one of them was kept in the retry queue, none were lost. Nothing else in your account was affected.

We replaced the certificate at 15:41 UTC and restarted the delivery workers at 15:47 UTC. Certificates now renew automatically 30 days before they expire, and if a renewal fails, the on-call engineer gets an alert 14 days before the expiry date. We're also adding a test delivery every 5 minutes, which would have caught this outage within minutes instead of the hour and a half it took us.

If your integration processed any of the replayed webhooks twice, or you're missing one, please reply to this email with the event IDs and we'll look into it.

Sorry for the trouble,
The Fernpost team
