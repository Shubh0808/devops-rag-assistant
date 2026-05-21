# INC-2025-001 Payment API Latency

## Summary

On 2025-02-14, the payment API p95 latency increased from 250 ms to 2.4 seconds.
Checkout requests started timing out for a small percentage of users.

## Impact

Checkout success rate dropped by 7 percent for 18 minutes.
No payment data was lost.

## Timeline

- 10:05 Alert fired for payment API p95 latency.
- 10:08 On-call engineer checked application metrics and saw database latency increase.
- 10:12 Slow query dashboard showed a new query scanning the `payments` table.
- 10:17 Feature flag for the new payment search filter was disabled.
- 10:23 p95 latency returned to normal.

## Root Cause

A new payment search filter generated a database query that did not use an index.
The query caused high database CPU and exhausted the API connection pool.

## Resolution

The feature flag was disabled.
The team added an index for the new search field and added a regression test for the query plan.

## Follow-Up Actions

- Add query plan review for payment search changes.
- Add dashboard panel for payment database connection pool usage.
- Update the API latency runbook with connection pool checks.

