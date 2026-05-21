# Kubernetes CrashLoopBackOff Runbook

## Symptoms

The pod repeatedly starts and exits. Kubernetes shows the pod status as `CrashLoopBackOff`.
Users may see failed requests if the crashing pod is part of a service with too few healthy replicas.

## First Checks

1. Check the current pod state with `kubectl get pods -n <namespace>`.
2. Describe the pod with `kubectl describe pod <pod-name> -n <namespace>`.
3. Read the previous container logs with `kubectl logs <pod-name> -n <namespace> --previous`.
4. Check recent deployment changes, image tags, ConfigMaps, Secrets, and environment variables.

## Common Causes

- Missing environment variable or secret.
- Application starts before a dependency is ready.
- Incorrect container command or entrypoint.
- Failed database connection during startup.
- Memory limit too low, causing the container to be killed.

## Resolution Steps

If logs show a missing configuration value, restore the ConfigMap or Secret and restart the deployment.
If the container is killed because of memory, compare the current memory limit with historical usage and increase it carefully.
If the app cannot connect to a dependency, verify service DNS, network policy, credentials, and dependency health.

## Validation

Confirm that the pod reaches `Running` state, readiness checks pass, and error rate returns to normal.
Monitor logs for at least 10 minutes after the fix.

