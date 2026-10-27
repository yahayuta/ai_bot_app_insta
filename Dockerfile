# Copyright 2020 Google, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START cloudrun_helloworld_dockerfile]
# [START run_helloworld_dockerfile]

# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.10-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies.
# Install everything in one pip run so the resolver sees every constraint at once.
# stability-sdk needs protobuf<6, while the newest googleapis-common-protos
# (1.76+) needs protobuf>=6.33.5. Separate pip runs let them overwrite each other
# and the app then fails at import time ("Worker failed to boot").
RUN pip install --no-cache-dir -r requirements.txt \
    requests \
    "openai<3" \
    "google-cloud-storage<4" \
    "stability-sdk==0.8.6" \
    "google-genai<2" \
    "pillow<13" \
    "protobuf<6" \
    "googleapis-common-protos<1.76"

# Fail the build (instead of the running service) if the app cannot be imported.
# A failed build keeps the current revision serving traffic.
RUN OPENAI_TOKEN=build-check python -c "import main"

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app

# [END run_helloworld_dockerfile]
# [END cloudrun_helloworld_dockerfile]
