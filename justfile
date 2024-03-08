separate-compose := "command -v docker-compose 2>/dev/null"

init:
    if [ ! -f requirements.lock ]; then rye sync; fi
    rye run pre-commit install
    docker build -t gprk-base:latest .
    if {{ separate-compose }};     \
        then docker-compose build; \
        else docker compose build; \
    fi

start:
    if {{ separate-compose }};  \
        then docker-compose up; \
        else docker compose up; \
    fi

stop:
    if {{ separate-compose }};    \
        then docker-compose down; \
        else docker compose down; \
    fi

format:
    rye run ruff format
    rye run ruff check --fix # sort headers + lintint
