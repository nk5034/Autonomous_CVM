# Kubernetes Manifests

## Structure

- `base/`: common application resources.
- `overlays/dev`: DEV customization.
- `overlays/qa`: QA customization.
- `overlays/uat`: UAT customization.
- `overlays/prod`: PROD customization.

## Apply Example

```bash
kubectl apply -k infrastructure/kubernetes/overlays/dev
```

## Notes

- Replace image repository placeholders before apply.
- Prefer Helm-based deployment for enterprise release management and rollback.
