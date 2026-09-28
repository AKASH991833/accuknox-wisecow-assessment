# Wisecow - AccuKnox DevOps trainee assessment

This is a partial draft. The source app and Apache-2.0 license come from https://github.com/nyrahul/wisecow . `server.py` uses fortune and cowsay to serve valid HTTP on port 4499, with `/healthz` returning 200 and errors returning 503. The original upstream `wisecow.sh` is retained for reference.

The Dockerfile installs fortune-mod, cowsay and fortune data, runs as a non-root user. The Kubernetes Deployment and ClusterIP Service are in `k8s/wisecow.yaml`. The GitHub Actions workflow in `.github/workflows/image.yml` builds and pushes image tags to GHCR on main branch changes. The two selected scripting tasks are `scripts/log_report.py` (404s, top paths/IPs) and `scripts/health_check.py` (2xx up, other status or connection error down).

## Local checks

Six Python unit tests passed locally, plus Python syntax compilation, Bash syntax check and YAML parsing. Docker image build, running container, cluster deployment, GitHub workflow execution, TLS and KubeArmor were **not** tested. No live Kubernetes service exists yet. Optional automatic deployment and TLS are not implemented.

## Run and test on a machine with Docker

```sh
docker build -t wisecow:local .
docker run --rm -p 4499:4499 wisecow:local
curl -i http://localhost:4499/healthz
curl -i http://localhost:4499/
python3 -m unittest discover -s tests -v
```

For Kubernetes, first replace the placeholder image `ghcr.io/OWNER/REPOSITORY:main` in `k8s/wisecow.yaml` with the actual built/published image, then `kubectl apply -f k8s/wisecow.yaml`, check `kubectl rollout status deployment/wisecow`, and `kubectl port-forward service/wisecow 8080:80`. Private GHCR images require an imagePullSecret; credentials must not be committed to the repo. This draft needs an actual image build and cluster verification before anyone claims it is deployed.
