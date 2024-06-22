#!/bin/bash


if [[ $1 == "--dev" ]]; then
    uvicorn main:app --host 0.0.0.0 --port 8000 --log-level debug --reload
elif [[ $1 == "--test" ]]; then
    # If .env file exists make a backup
    if [[ -f .env ]]; then
        echo ".env file exists, making a backup"
        cp .env .env.bak
    fi
    # Copy test .env file
    cp tests/.env.test .env
    cd tests
    docker-compose -f ./compose/mobius-compose.yml up -d
    echo "mobius docker container started"
    docker-compose -f ./compose/postgres-compose.yml up -d
    echo "postgres docker container started"
    # Run tests
    echo "Running tests"
    pytest --disable-warnings

    # return non zero exit code if tests fail
    test_exit_code=$?

    # Kill test om2m
    docker-compose -f ./compose/om2m-compose.yml down --remove-orphans
    echo "om2m docker container removed"
    docker-compose -f ./compose/postgres-compose.yml down --remove-orphans
    echo "postgres docker container removed"
    docker volume prune -f
    echo "docker volumes pruned"
    # Delete test om2m db
    cd ..
    # Restore .env file
    if [[ -f .env.bak ]]; then
        echo "Restoring .env file"
        mv .env.bak .env
    fi

    if [[ $test_exit_code -ne 0 ]]; then
        exit 1
    fi
else
    # print the value of the WORKERS environment variable
    echo "WORKERS: ${WORKERS:-1}"
    gunicorn main:app --workers=${WORKERS:-1} -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --preload
fi
