separate-compose := "command -v docker-compose 2>/dev/null"

# TODO: add compose variable to avoid branching in every recipe
# TODO: add clean recipe? or re-init? right now its
# `docker system prune -a && just init`

init:
    if [ ! -f requirements.lock ]; then rye sync; fi
    rye run pre-commit install
    docker build -t isat-cv-base:latest .
    if {{ separate-compose }};     \
        then docker-compose build; \
        else docker compose build; \
    fi

start service="":
    if {{ separate-compose }};  \
        then docker-compose up {{ service }}; \
        else docker compose up {{ service }}; \
    fi

stop service="":
    if {{ separate-compose }};    \
        then docker-compose down {{ service }}; \
        else docker compose down {{ service }}; \
    fi

format:
    rye run ruff format
    rye run ruff check --fix # sort headers + lint
