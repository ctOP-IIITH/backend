#!/bin/bash


if [[ $1 == "--dev" ]]; then
    uvicorn main:app --host 0.0.0.0 --port 8000 --log-level debug --reload
elif [[ $1 == "--test" ]]; then
    # Spin up test om2m
    echo "Starting test om2m"
    cd tests
    # This is for linux distro, if windows comment lines till 22 and manually start om2m
    cd test-om2m
    # check if java is 1.8.x
    java_version=$(java -version 2>&1 | awk -F '"' '/version/ {print $2}')
    if [[ $java_version != 1.8.* ]]; then
        echo "Java version is not 1.8.x"
        exit 1
    fi

    java -jar -ea -Declipse.ignoreApp=true -Dosgi.clean=true -Ddebug=true plugins/org.eclipse.equinox.launcher_1.3.0.v20140415-2008.jar -console -noExit &
    om2m_pid=$!
    echo "Test om2m started with pid: $om2m_pid"
    cd ..
    # Run tests
    echo "Running tests"
    pytest --disable-warnings
    # return non zero exit code if tests fail
    test_exit_code=$?
    # Kill test om2m
    echo "Killing test om2m"
    kill -9 $om2m_pid
    echo "Test om2m killed"
    # Delete test om2m db
    echo "Deleting test om2m db"
    rm -rf test-om2m/database/
    rm -r test.db
    # Wait for all extra files to be deleted
    echo "Waiting for all extra files to be deleted"
    sleep 5
    if [[ $test_exit_code -ne 0 ]]; then
        exit 1
    fi
else
    # print the value of the WORKERS environment variable
    echo "WORKERS: ${WORKERS:-1}"
    gunicorn main:app --workers=${WORKERS:-1} -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --preload
fi
