set shell := ["bash", "-c"]

start arg:
    docker compose up {{arg}} --build -d

cleanup:
    docker compose down --remove-orphans
