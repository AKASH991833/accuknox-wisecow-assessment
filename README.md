# Wisecow - AccuKnox DevOps assessment

This repository adapts the [upstream Wisecow](https://github.com/nyrahul/wisecow) Bash script into a small HTTP service. The upstream `wisecow.sh` and Apache-2.0 license are retained. The Python wrapper runs the same `fortune`/`cowsay` commands, returns valid HTTP responses, escapes generated HTML, and exposes a health endpoint.

## What is included

- `server.py`: `/` serves cow wisdom, `/healthz` returns `200 ok`, unknown paths return 404, and failed command execution returns 503.
- `Dockerfile`: installs `fortune`, `cowsay`, and `netcat`; runs as UID 10001 on port 4499.
- `k8s/wisecow.yaml`: two replicas, resource limits, non-root security context, readiness/liveness probes, and a ClusterIP Service.
- `k8s/tls-proxy.yaml`: optional nginx TLS-terminating reverse proxy and Service. It requires a TLS Secret named `wisecow-tls` and is only a self-signed demonstration, not a trusted public endpoint.
- `.github/workflows/image.yml`: on a push to `main`, runs unit tests and a Kind deployment smoke test, builds and publishes `main` and commit-SHA image tags to GitHub Container Registry, and tests HTTPS through the proxy inside Kind.
- `scripts/log_report.py`: summarizes combined-format access logs, including requests, 404s, popular paths/IPs, and malformed rows.
- `scripts/health_check.py`: checks an HTTP(S) URL and exits 0 for a 2xx response or 1 when down.

## Run locally

```sh
docker build -t wisecow:local .
docker run --rm -p 4499:4499 wisecow:local
curl -i http://localhost:4499/healthz
curl -i http://localhost:4499/
python3 -m unittest discover -s tests -v
```

## Run in Kubernetes

Set `ghcr.io/OWNER/REPOSITORY:main` in `k8s/wisecow.yaml` to the correct lowercase image name and make sure the image is accessible to the cluster. For a private package, configure an image pull secret rather than committing credentials. Then:

```sh
kubectl apply -f k8s/wisecow.yaml
kubectl rollout status deployment/wisecow
kubectl port-forward service/wisecow 8080:80
curl -i http://localhost:8080/healthz
```

For local Kind testing, build `wisecow:local`, load it with `kind load docker-image wisecow:local`, and change the manifest image to `wisecow:local` with `imagePullPolicy: IfNotPresent`. The CI workflow automates that ephemeral Kind test.

The optional TLS proxy needs a certificate and key in the `wisecow-tls` Kubernetes Secret before applying `k8s/tls-proxy.yaml`. For a real deployment, use a trusted certificate, DNS, and a suitable ingress or load-balancer setup. The self-signed certificate generated during CI lives only in the temporary Kind cluster. It is **not** an internet-accessible HTTPS deployment.

## Verification and limits

Six Python unit tests passed. GitHub Actions built/published the image, deployed it into temporary Kind, and checked both `/healthz` and `/` over HTTP in this [passing run](https://github.com/AKASH991833/accuknox-wisecow-assessment/actions/runs/36382484429). A later [passing run](https://github.com/AKASH991833/accuknox-wisecow-assessment/actions/runs/36382760961) verified HTTPS `/healthz` through nginx with a self-signed certificate in temporary Kind. Both its image and cluster-smoke jobs succeeded. The image-publish job and Kind tests run independently, so the Kind test checks a locally built image, not a pull of the published registry package.

This is an assessment repository, not a continuously hosted service. Automated deployment to an external cluster, a trusted public TLS endpoint, and the optional KubeArmor policy are not implemented. The `main` tag is replaced on each push; use a commit-SHA tag for a fixed version.

## Scripts

```sh
python3 scripts/log_report.py /var/log/nginx/access.log --top 5
python3 scripts/health_check.py http://localhost:4499/healthz --timeout 5
```

Upstream: https://github.com/nyrahul/wisecow (Apache-2.0). See `LICENSE`.
