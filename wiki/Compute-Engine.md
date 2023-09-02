# Deploying LLaMA models to Google Compute Engine

## Setup

### Google Cloud project setup

* Enable the Google Compute Engine API:
    ```bash
    gcloud services enable compute.googleapis.com
    ```

### Creating a Google Compute Engine VM instance to get the CUDA version

This step is only for confirming the CUDA version compatible with the cloud GPU. For the Nvidia T4 GPUs I am using it is `11.4`. If you already know what the CUDA version is, you can skip this step. 

#### Creating the instance

* Go to [***Google Compute Engine***](https://console.cloud.google.com/compute/) and create a new VM instance.
* Name your VM instance.
* Select a region and zone. The price and availability of hardware can vary depending on these values.
* Select the `GPUs` configuration.
* Choose a GPU with enough memory to load your model. For my 13b model, that is 10GB max, so I used one *NVIDIA T4*.
* Scroll down to the `Boot disk` section and click on `CHANGE`.
* Change the OS to `Container Optimized OS`.
* Change the size to `100`.
* Click on `SELECT`.
* Click on `Advanced options` => `Networking` => `default` => `External IPv4 address` => `RESERVE STATIC EXTERNAL IP ADDRESS`.
* Create your VM instance!
> NOTE: You may get errors that there's no availability in your current zone. If you do, you will have to follow these steps from the start with a different region/zone.

#### Setting up the instance

* Once the VM instance is up and running, click on the `SSH` button next to it's name and zone.
* Once the SSH window opens and authenticates, run:
	```bash
	sudo cos-extensions install gpu
	sudo mount --bind /var/lib/nvidia /var/lib/nvidia
	sudo mount -o remount,exec /var/lib/nvidia
	```
* This will install the GPU drivers for your VM. To see the driver info, run:
	```bash
	/var/lib/nvidia/bin/nvidia-smi
	```
* You should see something like:
	```bash
	+-----------------------------------------------------------------------------+
	| NVIDIA-SMI 470.199.02   Driver Version: 470.199.02   CUDA Version: 11.4     |
	|-------------------------------+----------------------+----------------------+
	| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
	| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
	|                               |                      |               MIG M. |
	|===============================+======================+======================|
	|   0  Tesla T4            Off  | 00000000:00:04.0 Off |                    0 |
	| N/A   70C    P0    33W /  70W |      0MiB / 15109MiB |      0%      Default |
	|                               |                      |                  N/A |
	+-------------------------------+----------------------+----------------------+
	
	+-----------------------------------------------------------------------------+
	| Processes:                                                                  |
	|  GPU   GI   CI        PID   Type   Process name                  GPU Memory |
	|        ID   ID                                                   Usage      |
	|=============================================================================|
	|  No running processes found                                                 |
	+-----------------------------------------------------------------------------+
	```
* Remember the `CUDA Version`.

#### Deleting the instance

* Exit the SSH window.
* Go back to the Google Compute Engine page, click on your VM instance and click `DELETE`.

### Updating the scripts

* Go to the [***tags section of the NVIDIA/CUDA Docker image site***](https://hub.docker.com/r/nvidia/cuda/tags) and filter the tags with the `CUDA Version` you got before.
* Copy the name of the latest tag which follows the format: `[CUDA Version].[Any minor version]-devel-ubuntu[Ubuntu version, usually 20.04]`.
* In `Dockerfile` change line **6** to `FROM nvidia/cuda:` and paste the tag your copied in the previous step after the colon (`:`).

## Building, testing and uploading the Docker image

There is no easy way to test the image locally.
If you have Admin SDK authentication enabled, you will **have** to set `USE_FIREBASE_ADMIN_AUTH` to `False` to disable it, build the image, upload the image and test it using cURL from your PC. Once you're ready to upload the "production" version to Google Cloud Run, set it back to `True` and build the image again.

### Building and uploading the image

* To build the image, replace `REGION`, `PROJECT`, `REPOSITORY` and `IMAGE_NAME` with your desired values and run:<br/>
    * Command Prompt (Windows)
    	```cmd
    	SET VERSION="1.2.10"
    	SET REGION="Google Cloud Platform region"
    	SET PROJECT="Google Cloud project ID"
		SET REPOSITORY="Google Cloud Artifact Registry repository name"

		REM The below line will make the image name the same as the repository name. To change it, replace %REPOSITORY% with the name.
    	SET IMAGE_NAME=%REPOSITORY%

		SET NAME="%REGION%-docker.pkg.dev/%PROJECT%/%REPOSITORY%/%IMAGE_NAME%:%VERSION%"

    	docker build -t %NAME% .
    	```
    * Bash
		```bash
		export VERSION="1.2.10"
		export REGION="Google Cloud Platform region"
		export PROJECT="Google Cloud project ID"
		export REPOSITORY="Google Cloud Artifact Registry repository name"

		# The below line will make the image name the same as the repository name. To change it, replace $REPOSITORY with the name.
		export IMAGE_NAME=$REPOSITORY

		export NAME="$REGION-docker.pkg.dev/$PROJECT/$REPOSITORY/$IMAGE_NAME:$VERSION"

		docker build -t $NAME .
		```
* To push the image to the Google Cloud Artifact Registry, run:
    * Command Prompt (Windows)
		```cmd
    	docker push %NAME%
    	```
    * Bash
		```bash
		docker push $NAME
		```
* Get the link to your image by printing out the `NAME` variable and copying it:
    * Command Prompt (Windows)
		```cmd
    	echo %NAME%
    	```
    * Bash
		```bash
		echo $NAME
		```

### Deploying the image

* Follow the steps to create a new VM instance defined in the [***Creating a Google Compute Engine VM instance to get the CUDA version***](https://github.com/Uralstech/vid-orca/wiki/LLaMA-On-Google-Compute-Engine#creating-the-instance) section, but also follow these steps:
	* Before creating the image, in the `Container` section, click on `DEPLOY CONTAINER` and:
		* Paste the link to your image in the `Container image` box.
		* Check `Run as privileged`, `Allocate a buffer for STDIN` and `Allocate a pseudo-TTY`.
		* Set the command to `docker run -p 8080:8080 ` and then the link to your image.
	* In the `Management` section:
		* In the `Automation` box paste:
			```bash
			#!/bin/bash
			sudo cos-extensions install gpu
			sudo mount --bind /var/lib/nvidia /var/lib/nvidia
			sudo mount -o remount,exec /var/lib/nvidia
			docker run \
			  --volume /var/lib/nvidia/lib64:/usr/local/nvidia/lib64 \
			  --volume /var/lib/nvidia/bin:/usr/local/nvidia/bin \
			  --device /dev/nvidia0:/dev/nvidia0 \
			  --device /dev/nvidia-uvm:/dev/nvidia-uvm \
			  --device /dev/nvidiactl:/dev/nvidiactl \
			  -p 8080:8080 
			```
		* And at the end of the text also paste in the link to your image.
* It may take some time for the image to appear in the VM instance. To check if it has, you can SSH into the instance and run run:
	```bash
	docker images
	```
	* You should see your image and version tag in the list.
* If there is an error at the beginning of the SSH in a red box of hashs (`#`), you can manually start the image by:
	* Clicking on `EDIT` in your VM instance on Google Compute Engine.
	* Copying the text in the `Automation` box under the `Management` section.
	* Pasting the text in the SSH window and pressing enter.

### Testing the deployment

* You can now test the deployment by opening a new terminal window on your PC and running:
    * Command Prompt (Windows)
		```cmd
    	curl -X POST "http://localhost:8080/api/chat" ^
    	-H  "accept: application/json" ^
    	-H  "Content-Type: application/json" ^
    	-d "{\"messages\":[{\"role\":\"system\",\"content\":\"You are a helpful assistant AI.\"},{\"role\":\"user\",\"content\":\"Who made Linux?\"}]}"
    	```
    * Bash
		```bash
		curl -X POST "http://localhost:8080/api/chat" \
		-H "accept: application/json" \
		-H "Content-Type: application/json" \
		-d "{\"messages\":[{\"role\":\"system\",\"content\":\"You are a helpful assistant AI.\"},{\"role\":\"user\",\"content\":\"Who made Linux?\"}]}"
		```
* Once you get the output, you can rebuild the image with `USE_FIREBASE_ADMIN_AUTH` set to `True`, if you want to. It can also be helpful to set the `VERSION` variable (both in `main.py` and in the command to build the image) to something higher, to distinguish between versions of the image.

## Congrats!

You've deployed a `LLaMA` model to your Google Cloud project!