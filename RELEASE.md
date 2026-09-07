# How to ship a Merge Cheer release

A Marketplace-facing Release is **tests plus a human review**. Pushing a
tag does not publish anything. GitHub also cannot tick the Marketplace
box through the API — this workflow only creates the GitHub Release.

## One-time: review environment

The `release` job uses `environment: marketplace`. That name does
nothing until a required reviewer exists.

1. Open [Settings → Environments](https://github.com/YauhenBichel/merge-cheer/settings/environments)
2. Create an environment named **`marketplace`** (exact spelling)
3. Enable **Required reviewers** and add at least one person
4. Save

Until that Settings click, the job will not wait for Approve.

## Cut a reviewed release

Land the work on the default branch. Wait until **CI / test** is green
on the commit you intend to ship. Then tag that commit. Semver only
(`vMAJOR.MINOR.PATCH`). Do not force-move `v1`.

```
git tag v1.2.0
git push origin v1.2.0
```

`v1` is the first tag on this repository, not a floating major this
workflow maintains. Consumers may keep `uses: YauhenBichel/merge-cheer@v1`
only if a human later chooses to move that tag. Never `git tag -f v1`
from automation.

1. Actions → **Release** → Run workflow
2. Use the default branch (or the tag itself)
3. Version input: `v1.2.0` (leading `v`, three numbers)
4. The **test** job checks out that tag and runs
   `python3 -m unittest discover -s tests -q`
5. If tests fail, stop. Nothing is published.
6. The **release** job then waits on the `marketplace` environment.
   Open the deployment review and click **Approve**.
7. The job creates the GitHub Release for that tag, or updates notes if
   the Release already exists (safe to re-run). `action.yml` is not an
   asset — the tag **is** the Action version.

## Marketplace

Listing: https://github.com/marketplace/actions/merge-cheer

The listing form needs a G-rated screenshot of a real merge comment
that uses a bundled GIF. Use [docs/marketplace.png](docs/marketplace.png)
(the [live #53 comment](https://github.com/YauhenBichel/merge-cheer/pull/53#issuecomment-5574024316)).

The first publish is a browser + 2FA step (no API). Prefer
Settings → Actions → **Publish this Action to the GitHub Marketplace**,
or:

https://github.com/YauhenBichel/merge-cheer/releases/edit/v1.6.0?marketplace=true

Later reviewed Releases update that listing automatically once it exists.

## Docker Hub + GitLab (from GitHub Actions)

1. **Docker Hub** — secrets `DOCKERHUB_USERNAME` (Hub username, not
   email) and `DOCKERHUB_TOKEN` (Access Token with Read & Write). Prefer
   `printf '%s' '…' | gh secret set …` so the value has no trailing
   newline. Workflows trim CR/LF before login. The **Release** workflow’s
   `docker` job pushes the image after the reviewed GitHub Release.
   Manual retry: Actions → **Publish Docker** → `v1.5.0`.
2. **GitLab Catalog** — create `YauhenBichel/merge-cheer` on GitLab,
   enable **CI/CD Catalog project**, then either configure a GitLab
   **pull mirror** or set `GITLAB_MIRROR_TOKEN` and run **Mirror to
   GitLab**. Tag pipelines on GitLab publish Catalog versions via the
   `release:` keyword.

Details: [MARKETPLACES.md](MARKETPLACES.md). Do not claim those rows
exist until their catalog URLs return 200.
