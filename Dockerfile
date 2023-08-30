# For GCE users:
#   The Cuda image will vary depending on your GPU driver.
#   To check which Cuda version is supported by your GPU, run nvidia-smi.
# For Cloud Run users:
#   Change this image to a Python image like python:3.11-slim or python:3.11-slim-bullseye.
FROM nvidia/cuda:11.4.3-devel-ubuntu20.04
ENV PYTHONUNBUFFERED True

# Remove the below 4 lines if you are using Cloud Run.
# This line tells Ubuntu/Debian to make the front-end non-interactive.
ENV DEBIAN_FRONTEND noninteractive
# This sets the timezone.
ENV TZ Etc/GMT
# The below line sets the cmake arguments to build LLaMA CPP and tells it to enable-
#     CUBLAS (CUDA Basic Linear Algebra Subprograms) which speeds up the models on GPUs.
ENV CMAKE_ARGS "-DLLAMA_CUBLAS=on"
# This forces pip to use cmake.
ENV FORCE_CMAKE 1

WORKDIR /vid-orca
COPY . .

# Remove the below line if you are using Cloud Run, as you have set the base image to a Python image.
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip

RUN apt-get update && apt-get install -y gcc build-essential cmake
RUN pip install -r requirements.txt
RUN pip install llama-cpp-python==0.1.81 --no-cache-dir

# Uncomment the below line to install the nano text editor for debugging (only useful in GCE Virtual Machines).
# RUN apt-get update && apt-get install -y nano

WORKDIR /vid-orca/src

# For Firebase Admin SDK authentication users using GCE:
#   Change the below line to the absolute path to your Firebase Admin SDK Service Account key file.
# For others:
#   Remove the below line. (If you are using Cloud Run, this is already set up for you)
ENV GOOGLE_APPLICATION_CREDENTIALS "/vid-orca/NOCOMMIT/Keys/admin-sdk-key.json"

CMD exec uvicorn main:app --host 0.0.0.0 --port 8080 --workers 1