#!/usr/local/bin/ python
from time import time
import os
import io
import json
import requests
import subprocess
import zipfile

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


"""
README
---
LABEL name="code-quality" \
      maintainer="Mat McCann <matmccann@gmail.com>" \
      version="1.0" \
      description="Loadtest and lighthouse analysis are performed based on exported environment variables."
DOCKERHUB: https://cloud.docker.com/repository/docker/superelectron/code-quality

EXPORT VARIABLES
LOCAL-SETUP:
   - docker pull superelectron/code-quality:tag
   - docker images ls
   - docker run superelectron/code-quality:tag
   - docker exec -it [image-tag] ./bin/sh
   - export LOADTIME_THRESHOLD="5"
   - export HOST_ADDRESS="https//:www.your-url.com" && export POST_URL="url/to/post"
   - export AUTH_HEADER="some-auth-password"
   - export PAYLOAD_PATH="path/to/payload.json"
   - export CI_ROOT="/"
   - cd code
   - python -m code-quality
   - python -m test_script

CI-PIPELINE
    - commit your docker "container" to your gitlab project assuming its container name is "code-quality" like in the
    docker-compose.yml. Verify this with $ docker ps from your command line.project

    - Below is an example ci-setup
    - note that the runner you choose (tags: Deploy) must be able to connect to the external world!
    
code-quality:
  stage: post
  allow_failure: true
  image: [name of your gitlab-ci container registry name]
  tags:
    - Deploy # use a runner that can connect with the external world!
  variables:
    LOADTIME_THRESHOLD: 5
    HOST_ADDRESS: "https//:www.your-url.com"
    POST_URL: "url/to/post" # appends to HOST_ADDRESS
    AUTH_HEADER: "some-auth-password"
    PAYLOAD_PATH: "path/to/payload.json"
    CI_ROOT: "/builds/gitlab-ci-project-root"
  script:
    - echo $LOADTIME_THRESHOLD
    - echo "posting data to ---> $HOST_ADDRESS/$POST_URL"
    - echo $PAYLOAD_PATH
    - cd $CI_SCRIPTS
    - python -m code-quality
  artifacts:
    untracked: false
    name: "$CI_JOB_NAME-$CI_COMMIT_REF_NAME"
      - $CI_ROOT/lighthouse-reports.csv
"""
def time_it(func):
    def wrapper(*arg,**kw):
        t1 = time()
        response = func(*arg,**kw)
        t2 = time()
        return (t2-t1), response
    return wrapper


def get_perf_measure(driver, url, display=True):
    driver.get(url)
    navigationStart = driver.execute_script("return window.performance.timing.navigationStart")
    responseStart = driver.execute_script("return window.performance.timing.responseStart")
    domComplete = driver.execute_script("return window.performance.timing.domComplete")
    backendPerformance_calc = responseStart - navigationStart
    frontendPerformance_calc = domComplete - responseStart
    if(display):
        print("backend Performance_calc = responseStart - navigationStart: ", backendPerformance_calc)
        print("frontend Performance_calc = domComplete - responseStart: ", frontendPerformance_calc)
    return [backendPerformance_calc, frontendPerformance_calc]

@time_it
def post_perf_measure(url, data, header):
    return requests.post(url, data=json.dumps(data), headers=header)


def import_payload(project_root, file_path, display=False):
    try:
        original_directory = os.getcwd()
        os.chdir(project_root)
        with open(file_path) as f:
            data = json.load(f)

        if(display):
            print("payload\n{}".format(json.dumps(data, indent=2, sort_keys=True)))
        os.chdir(original_directory)
        return data
    except:
        print("ERROR: payload path not read relative to project root:{}".format(file_path))
        print("os.getcwd():{}".format(os.getcwd()))
        print("project root:{}".format(project_root))
        exit(1)


def import_environment_variables():
    try:
        PROJECT_ROOT = os.environ['CI_ROOT']
        LOADTIME_THRESHOLD = os.environ['LOADTIME_THRESHOLD']
        ENDPOINT_CREDS = os.environ['AUTH_HEADER']
        PAYLOAD_PATH = os.environ['PAYLOAD_PATH']
        HOST_ADDRESS = os.environ['HOST_ADDRESS']
        POST_URL = os.environ['POST_URL']

        return PROJECT_ROOT, LOADTIME_THRESHOLD, ENDPOINT_CREDS, PAYLOAD_PATH, HOST_ADDRESS, POST_URL
    except:
        if None in [PROJECT_ROOT, LOADTIME_THRESHOLD, ENDPOINT_CREDS, PAYLOAD_PATH, HOST_ADDRESS, POST_URL]:
            print("environment variable(s) not found: ", \
                "LOADTIME_THRESHOLD:{}".format(LOADTIME_THRESHOLD), "  ", \
                "TELUS_API_ENDPOINT_CREDS:{}".format(ENDPOINT_CREDS), "  ", \
                "PAYLOAD_PATH:{}".format(PAYLOAD_PATH), "  ", \
                "HOST_ADDRESS:{}".format(HOST_ADDRESS), "  ", \
                "POST_URL:{}".format(POST_URL)
            )
        exit(1)


def main():
    print("\n\n*****************\nLOADING DATA AND ENVIRONMENT VARIABLES")
    PROJECT_ROOT, LOADTIME_THRESHOLD, ENDPOINT_CREDS, PAYLOAD_PATH, HOST_ADDRESS, POST_URL = import_environment_variables()
    # pass payload path relative to the project root & load it
    post_data = import_payload(PROJECT_ROOT, PAYLOAD_PATH, display=False)
    post_address = HOST_ADDRESS + "/" + POST_URL

    headers = {
    "Accept": "*/*",
    "Cache-Control": "no-cache",
    "Content-Type": "application/json",
    "Authorization": ENDPOINT_CREDS,
    "Cookie": "XDEBUG_SESSION=PHPSTORM"
    }

    time, response = post_perf_measure(post_address, post_data, headers)
    print("Load time threshold:", LOADTIME_THRESHOLD)
    print("post request time {}".format(time))
    print("http url {}\nresponse: {}\nresponse body\n{}\n\nheaders\n{}\n".format(response.url, response.status_code, response.text, response.headers))

    try:
        url = json.loads(response.text)['cartUri']
    except TypeError as err:
        print(err)
        exit(1)

    # Testing DOM and load times for webpage
    print("\n\n*****************\nSELENIUM PERFORMANCE INDICATORS")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)
    get_perf_measure(driver, str(url), display=True)
    driver.quit()

    print("\n\n*****************\nSTARTING LIGHTHOUSE TEST\n")
    lighthouse_command = "lighthouse " + str(url) + " --chrome-flags='--headless --no-sandbox' --output csv --[no-]enable-error-reporting " + "--output-path " + PROJECT_ROOT +  '/lighthouse-reports.csv'
    print(lighthouse_command)
    subprocess.call(lighthouse_command, shell=True)

    if(time < int(LOADTIME_THRESHOLD)):
        print("\n\nPASS load-time test")
        exit(0)
    else:
        print("\n\nFAIL load-time test")
        exit(1)


if __name__ == '__main__':
    main()
