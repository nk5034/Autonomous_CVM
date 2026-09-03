# Helm Deployment

## Chart

- Path: `infrastructure/helm/cvm-catalyst`
- Release name default: `cvm-catalyst`

## Deploy Example

```bash
helm upgrade --install cvm-catalyst infrastructure/helm/cvm-catalyst \
  -n cvm-catalyst-dev --create-namespace \
  -f infrastructure/helm/cvm-catalyst/values.yaml \
  -f infrastructure/helm/cvm-catalyst/values-dev.yaml \
  --set images.backend.tag=sha-example \
  --set images.frontend.tag=sha-example
```

## Rollback Example

```bash
helm rollback cvm-catalyst 12 -n cvm-catalyst-dev
```
