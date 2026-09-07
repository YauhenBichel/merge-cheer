# List Merge Cheer on GitLab and Bitbucket

The GitHub Action stays the source. GitLab and Bitbucket reuse
`src/celebrate.py`. GIFs stay on GitHub raw URLs. This file is the
listing work a human still has to do — neither catalog can be fully
ticked from GitHub alone (no Marketplace MCP; GitHub Marketplace itself
still needs a browser + 2FA tick).

Do not claim a listing is live until the catalog URL returns 200.

Automation already in this repo:

| Workflow | What it does | Secrets |
|----------|--------------|---------|
| [Release](.github/workflows/release.yml) (`docker` job) | Push Hub image after reviewed Release | `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN` |
| [Publish Docker](.github/workflows/publish-docker.yml) | Manual Hub retry | same |
| [Mirror to GitLab](.github/workflows/mirror-gitlab.yml) | Push tags/main to GitLab (optional) | `GITLAB_MIRROR_TOKEN` (optional `GITLAB_PROJECT_PATH`) |

## GitLab CI/CD Catalog

GitLab’s marketplace is the [CI/CD Catalog](https://gitlab.com/explore/catalog).
A component project must live **on GitLab**. GitHub cannot publish into
that catalog via API.

### One-time setup

1. Create a public GitLab project: `YauhenBichel/merge-cheer`
   (namespace must match your GitLab username).
2. Choose **one** sync path:
   - **Preferred:** GitLab → Settings → Repository → Mirroring
     repositories → Pull from
     `https://github.com/YauhenBichel/merge-cheer.git` (mirror tags).
   - **Or:** add GitHub secret `GITLAB_MIRROR_TOKEN` (Project Access
     Token with `write_repository` + `api`) and rely on
     **Mirror to GitLab**. Optional secret `GITLAB_PROJECT_PATH`
     (default `YauhenBichel/merge-cheer`).
3. Set a project description. Keep `README.md` and
   `templates/merge-cheer.yml`.
4. Settings → General → Visibility → **CI/CD Catalog project** (Owner).
5. Add a project access token named `GITLAB_TOKEN` with `api` scope for
   consumers (posting MR notes). `CI_JOB_TOKEN` cannot post notes.

### Publish a Catalog version

Push or mirror semver tag `v1.6.0`. `.gitlab-ci.yml` runs tests, then a
`release:` job. **GitLab only indexes versions created with that
keyword** (not the Releases REST API alone).

```yaml
include:
  - component: $CI_SERVER_FQDN/YauhenBichel/merge-cheer/merge-cheer@v1.6.0
    inputs:
      topic: auto
      token: $GITLAB_TOKEN
```

Until the catalog row exists, consumers can copy
[examples/gitlab-ci.yml](examples/gitlab-ci.yml).

## Bitbucket Pipes

Bitbucket’s directory is [Pipes](https://support.atlassian.com/bitbucket-cloud/docs/what-are-pipes/).
A usable pipe needs a **public Docker image**. The UI catalog is separate.

### Docker Hub (automatable from GitHub)

1. Create a Docker Hub account / namespace that will own the pipe image.
2. Add GitHub Actions secrets:
   - `DOCKERHUB_USERNAME` — Hub **username** (not email)
   - `DOCKERHUB_TOKEN` — Hub **Access Token** (Read & Write), no newline
3. Run Actions → **Release** with version `v1.6.0` (docker job pushes),
   or Actions → **Publish Docker** for a retry.
4. Keep `pipe.yml` pointing at that image (tag without the leading `v`).

### Consumers

Store `BITBUCKET_ACCESS_TOKEN` on the consumer repo (pullrequest write):

```yaml
script:
  - pipe: docker://eugenebichel/merge-cheer:1.6.0
    variables:
      TOPIC: auto
      BITBUCKET_ACCESS_TOKEN: $BITBUCKET_ACCESS_TOKEN
```

Until the image exists, use the curl job in
[examples/bitbucket-pipelines.yml](examples/bitbucket-pipelines.yml).

### Official Pipelines UI catalog (human review)

Open a PR against [official-pipes](https://bitbucket.org/atlassian/official-pipes)
with a `pipes/merge-cheer.yml` manifest. There is **no API** to skip that
review. Atlassian merges it before the pipe appears in the Pipelines UI.

## GitHub Marketplace

Listed: https://github.com/marketplace/actions/merge-cheer

First publish was a browser + 2FA tick (no API). Later releases update
that listing. See [RELEASE.md](RELEASE.md).
