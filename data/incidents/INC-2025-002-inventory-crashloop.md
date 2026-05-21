# INC-2025-002 Inventory Service CrashLoopBackOff

## Summary

On 2025-03-09, the inventory service pods entered `CrashLoopBackOff` after a deployment.
The service had enough replicas to avoid a full outage, but stock updates were delayed.

## Impact

Inventory updates were delayed for 11 minutes.
Users could still browse products, but stock counts were temporarily stale.

## Timeline

- 15:30 Deployment completed for inventory service version `1.18.0`.
- 15:32 Kubernetes alert fired for CrashLoopBackOff.
- 15:34 Previous container logs showed `Missing required environment variable: INVENTORY_DB_URL`.
- 15:37 On-call restored the missing Secret key.
- 15:41 Deployment restarted and pods became healthy.

## Root Cause

The deployment expected `INVENTORY_DB_URL`, but the Kubernetes Secret was missing that key in production.

## Resolution

The missing Secret key was restored and the deployment was restarted.

## Follow-Up Actions

- Add startup validation for required environment variables.
- Add CI check to compare required configuration with Kubernetes manifests.
- Update the CrashLoopBackOff runbook with `kubectl logs --previous`.

