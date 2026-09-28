# Wisecow - AccuKnox DevOps assessment draft

This is a review copy, not a deployed service. It retains the upstream `wisecow.sh` and adds an HTTP wrapper around the same `fortune`/`cowsay` output. The upstream script uses a named pipe and netcat; the wrapper provides valid HTTP responses, a health endpoint, explicit errors, and HTML escaping.

## Contents

- `server.py` serves `/` (cow wisdom) and `/healthz` (200 `ok`); other paths return 404. Missing/broken command execution returns 503.
- `Dockerfile` installs the tools, exposes port 4499, runs as UID 10001. `fortunes-min` supplies fortune data. The Debian packages place commands under `/usr/games`, added to `PATH`.
- `k8s/wisecow.yaml` defines two replicas, resource limits, non-root security, readiness/liveness probes and a ClusterIP Service on port 80.
- `.github/workflows/image.yml` builds and pushes `main` and commit-SHA tags to GitHub Container Registry on a push to `main`, with package-write permission.
- `scripts/log_report.py` analyzes combined-format Apache/Nginx logs (requests, 404s, popular paths and IPs). Bad rows are counted separately.
- `scripts/health_check.py` checks an HTTP(S) URL, prints UP only for 2xx, and exits 0 for UP or 1 for DOWN. Errors and timeouts count as DOWN.

## Run locally (requires Docker)

```sh
docker build -t wisecow:local .
docker run --rm -p 4499:4499 wisecow:local
curl -i http://localhost:4499/healthz
curl -i http://localhost:4499/
```

## Kubernetes setup (requires a configured cluster)

Replace `ghcr.io/OWNER/REPOSITORY:main` with the real lowercase registry image and publish an image before applying the manifest. A private image needs an appropriate Kubernetes `imagePullSecret` and a registry credential; do not paste credentials into manifests or a public repository. For a local Kind cluster instead, load the local image (`kind load docker-image wisecow:local`), change the manifest image to `wisecow:local` with `imagePullPolicy: IfNotPresent`, then apply:

```sh
kubectl apply -f k8s/wisecow.yaml
kubectl rollout status deployment/wisecow
kubectl port-forward service/wisecow 8080:80
curl -i http://localhost:8080/healthz
```

This service is **not TLS enabled**. The optional TLS challenge would need an Ingress controller, TLS Secret or cert-manager issuer, a DNS name, and an Ingress route. None are provided here, and no secure endpoint is claimed. Automatic deployment after image build and KubeArmor optional policy are also not implemented. A registry image was not built or pushed and no cluster deployment was run.

## Scripts

```sh
python3 scripts/log_report.py /var/log/nginx/access.log --top 5
python3 scripts/health_check.py http://localhost:4499/healthz --timeout 5
python3 -m unittest discover -s tests -v
```

Local checks completed in the preparation environment: six unit tests passed (two script tests and four HTTP-wrapper tests); Python compiled, Bash syntax check for upstream script passed, and the Kubernetes/workflow YAML parsed. These checks do not establish container build, cluster behavior, GitHub Actions execution, or public accessibility.

Upstream source: https://github.com/nyrahul/wisecow (Apache-2.0 licensed). The original source and license are retained. Public sharing and assignment submission are pending Akash's review and choice.
