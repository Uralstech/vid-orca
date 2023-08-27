# The Cuda image will vary depending on your GPU driver. To check which Cuda version is supported by your GPU, run nvidia-smi.
FROM nvidia/cuda:11.4.3-devel-ubuntu20.04
ENV PYTHONUNBUFFERED True
ENV DEBIAN_FRONTEND noninteractive
ENV TZ Etc/GMT
ENV CMAKE_ARGS "-DLLAMA_CUBLAS=on"
ENV FORCE_CMAKE 1

WORKDIR /vid-orca
COPY . .

RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip cmake
RUN apt-get update && apt-get install -y gcc build-essential
RUN pip install -r requirements.txt
RUN pip install llama-cpp-python==0.1.81 --no-cache-dir

# Uncomment the below line to install the nano text editor for debugging.
# RUN apt-get update && apt-get install -y nano

WORKDIR /vid-orca/src

# Change the below line to the absolute path to your Firebase Admin SDK Service Account key file.
ENV GOOGLE_APPLICATION_CREDENTIALS "/vid-orca/NOCOMMIT/Keys/admin-sdk-key.json"

CMD exec uvicorn main:app --host 0.0.0.0 --port 8080 --workers 1