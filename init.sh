if [ ! -f requirements.lock ]; then
	rye sync
fi

docker build -t isat-cv-base:latest . && docker-compose build