# Code Quality for Web Applications
- A basic image that can be used in to measure load-test and lighthouse analysis on your web application project.
- This document covers configuration of this image for your project.
- Check out dockerhub for the pre-built image: https://hub.docker.com/repository/docker/superelectron/loadtest-lighthouse
---

## Pulling the Image and Customizing it for Your Project
- pull the image and build it.
- this example is for a project named commerce!

```bash
$ docker pull superelectron/loadtest-lighthouse:latest
$ docker run superelectron/loadtest-lighthouse:latest
```

```bash
/commerce
    /scripts/ci
        /code
            code-quality.py
            requirements.txt
            test_script.py
        README.md
        docker-compose.yml
        Dockerfile
    /wwwroot
        /some-project-files
    docker-compose.yml
    gitlab-ci.yml
    Makefile
```

---

### Local Development and Setup for Your Project
- once your container is up and running verify image ID these two commands

```bash
$ docker images
$ docker ps
```
- can you see that the image ID from ```docker images``` lines up with that of ```docker ps```?
- if so, you are running, so continue

```bash
$ docker exec -it <containerID> /bin/bash
bash-4.4# ls
bin    code   dev    etc    home   lib    media  mnt    opt    proc   root   run    sbin   srv    sys    tmp    usr    var
```
- note that the scripts for this project are located in ```/code```.

#### Example in Docker Container
    LOADTIME_THRESHOLD: integer seconds for maximum loading time of web page
    POST_URL: path appended to URL (e.g. website.com/posts; /posts is POST URL)
    AUTH_HEADER: HTTP authorization header
    PAYLOAD_PATH: "/path/to/payload/file.json"
    CI_ROOT: "/path/to/code-quality.py"


```bash
$ export LOADTIME_THRESHOLD=5
$ export POST_URL="api/cart/add-a-line/add"
$ export AUTH_HEADER="670306112c4a192a57afb8eb3959da58d98f5001e48952c7ac0fc9fddd0d5327"
$ export PAYLOAD_PATH="/code/add-a-line.json"
$ export CI_ROOT="/"
$ export HOST_ADDRESS="https//:www.your-url.com"

```

- now let's run it!

```bash
$ cd code
$ python -m code-quality
$ python -m test_script
```

## Modifying My gitlab-ci.yml for a Pipeline

Noteworthy Points
1. the image is assume to be in your gitlab registry!
2. declare a basic setup to include "test" in your pipeline.
3. only should target the branch you are pushing, or on which branches you wish to run this test
5. ```tail -f /dev/null``` is used in ```Dockerfile``` to keep container running.  This can also be added into gitlab-ci under ```scripts``` so that you can debug the pipeline.
- Go to your container registry in gitlab: project >> packages >> container registry and view a similar Docker image path.

Example:
- git.company-name.com:xxxx/commerce/mysql
- replace 'mysql' with 'nightwatch' at the end like so, and build it:

```bash
$ docker run -t git.company-name.com:xxxx/commerce/loadtest-lighthouse
```

<br />

<br />

- Push the image to your project container registry
```bash
$ docker push git.company-name.com:xxxx/commerce/loadtest-lighthouse
```

#### CI-Pipeline Example
- commit your docker "container" to your gitlab project assuming its container name is "code-quality" like in the
    docker-compose.yml. Verify this with ```$ docker ps``` from your command line.
- note that the runner you choose (tags: Deploy) must be able to connect to the external world!

```bash
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
```

---

# TROUBLESHOOTING

---

## Troubleshooting the gitlab-ci pipeline
- keep ```tail -f /dev/null``` and when it hits that click ```debug```


- check to see if code-quality is setup: this will not pass if it isn't setup OR you may have a runner which cannot reach the external world!
- if this fails, change your gitlab-ci setup to have something either than ```tags: runner3```.  
- You can test the runner by trying ```curl www.google.ca``` after you open the debug terminal.


---

# CONTRIBUTING TO THE README.md
- here are some things that can help. Feel free to add points here if you think improvements can be made and push your suggestions to [github](https://github.com/SuperElectron/loadtest-lighthouse).


1. running code-quality tests in pipeline so that it tests actual site being pushed and not just some target branch.
2. basic Q&A put into the TROUBLESHOOTING 

---
