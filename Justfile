set shell := ["bash", "-c"]

hosts:
    @if ! grep -q '^127\.0\.0\.1[[:space:]]\+hutfinder\.localhost$' /etc/hosts; then \
        echo "Error: '127.0.0.1 hutfinder.localhost' not found in /etc/hosts."; \
        echo "Please add the following line to your /etc/hosts file:"; \
        echo "127.0.0.1 hutfinder.localhost"; \
        exit 1; \
    fi

caddy:
    sudo mkdir -p /etc/caddy
    sudo ln -sf {{invocation_directory()}}/dev.Caddyfile /etc/caddy/dev.Caddyfile
    sudo ln -sf {{invocation_directory()}}/prod.Caddyfile /etc/caddy/prod.Caddyfile

start arg: hosts
    just cleanup {{ arg }}
    CADDYFILE=/etc/caddy/{{ arg }}.Caddyfile docker compose up {{arg}} --build

cleanup arg:
    CADDYFILE=/etc/caddy/{{ arg }}.Caddyfile docker compose down --remove-orphans
