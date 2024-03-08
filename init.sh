if [ ! -f requirements.lock ]; then
	rye sync
fi

docker build -t isat-cv-base:latest .

if command -v docker-compose 2>/dev/null; then
    docker-compose build
else
    docker compose build
fi
