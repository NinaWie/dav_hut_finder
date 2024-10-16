set shell := ["bash", "-c"]

check-dev-hosts:
    @if ! grep -q '^127\.0\.0\.1[[:space:]]\+hutfinder\.localhost$' /etc/hosts; then \
        echo "Error: '127.0.0.1 hutfinder.localhost' not found in /etc/hosts."; \
        echo "Please add the following line to your /etc/hosts file:"; \
        echo "127.0.0.1 hutfinder.localhost"; \
        exit 1; \
    fi

start arg:
    @if [ "{{arg}}" = "dev" ]; then \
        just check-dev-hosts; \
    fi

    docker compose up {{arg}} --build

cleanup:
    docker compose down --remove-orphans
