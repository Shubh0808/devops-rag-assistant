# Database CPU Saturation Runbook

## Symptoms

Database CPU remains above 85 percent for more than 10 minutes.
Applications may show high latency, timeouts, or connection pool exhaustion.

## First Checks

1. Check active sessions and currently running queries.
2. Identify top CPU-consuming queries.
3. Check whether traffic increased unexpectedly.
4. Review recent schema changes, deployments, and batch jobs.
5. Check index usage and query execution plans.

## Common Causes

- Missing or unused index on a high-volume query.
- Batch job running during peak traffic.
- Query plan changed after data growth.
- Too many application connections.
- Reporting workload running on the primary database.

## Resolution Steps

Stop or reschedule non-critical batch jobs if they are causing load.
Add or fix indexes only after validating the query plan in a safe environment.
Reduce application connection pressure by tuning pool settings or scaling carefully.
Move reporting queries to a read replica when available.

## Validation

CPU should fall below the alert threshold, slow queries should reduce, and application latency should recover.

