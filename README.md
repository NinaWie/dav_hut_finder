# Alpenverein hut finder

Filter huts in the alps by
* distance from starting location
* Public transport accessibility
* Available places at a specific date

![](./doc/1.png)
![](./doc/2.png)

## Development

* work on `develop` branch by default
* use [conventional commit style for automatic semantic versioning and releases](https://engineering.deloitte.com.au/articles/semantic-versioning-with-conventional-commits) via CI
* install [pre-commit](https://pre-commit.com/) hook: `pre-commit install` to force correctness before every commit

### Docker

```
CADDYFILE=./dev.Caddyfile docker compose up dev --build
```

Open your browser at `hutfinder.localhost`

**Note:** `/etc/hosts` must include `127.0.0.1 hutfinder.localhost`
