# API Latency Spike Runbook

## Symptoms

The API p95 or p99 latency increases above the alert threshold.
Users may report slow page loads, request timeouts, or failed checkout actions.

## First Checks

1. Check application metrics for p95 latency, p99 latency, request rate, and error rate.
2. Compare current traffic with the same time yesterday and last week.
3. Check dependency latency for database, cache, payment gateway, and message broker calls.
4. Review recent deployments and feature flags.
5. Inspect pod CPU and memory usage.

## Common Causes

- Database queries became slow because of missing indexes or high CPU.
- Connection pool is exhausted.
- Cache hit rate dropped.
- A downstream dependency is timing out.
- A new deployment introduced inefficient code.

## Resolution Steps

If database latency is high, identify the top slow queries and check query plans.
If connection pool usage is near 100 percent, scale pods carefully or tune pool size after confirming database capacity.
If a downstream service is slow, enable fallback behavior or temporarily reduce traffic to the affected feature.
If a new deployment caused the spike, roll back to the last stable version.

## Validation

Confirm p95 latency returns below the service level objective, error rate is normal, and dependency latency is stable.

