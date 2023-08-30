# Deploying LLaMA models to Google Cloud Run

## Setup

### Updating the scripts

* In `main.py`, line **34**, remove `n_gpu_layers=43,` - including the comma. `n_gpu_layers` defines how much of the model to offload to your GPU, but as we are using Cloud Run, which does not have GPU processing, we don't need this.
* In `Dockerfile` remove lines **11**, **13**, **16**, **18**, **24** and **39**.
* Also in `Dockerfile`, change line **6** to `FROM python:3.11-slim-bullseye`.

### Google Cloud project setup

* Enable the Google Cloud Run API:
    ```bash
    gcloud services enable run.googleapis.com
    ```

## Building, testing and uploading the Docker image

If you want to test/run the image locally and have Admin SDK authentication enabled, you will **have** to set `USE_FIREBASE_ADMIN_AUTH` to `False` to disable it. This is the easiest way to test the service. Once you're ready to upload it to Google Cloud Run, set it back to `True` and build the image again.

* Replace `REGION`, `PROJECT`, `REPOSITORY` and `IMAGE_NAME` with your desired values an run:<br/>
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
    	docker run -p 8080:8080 %NAME%
    	```
    * Bash
		```bash
		export VERSION="1.2.7"
		export REGION="Google Cloud Platform region"
		export PROJECT="Google Cloud project ID"
		export REPOSITORY="Google Cloud Artifact Registry repository name"

		# The below line will make the image name the same as the repository name. To change it, replace $REPOSITORY 	with the name.
		export IMAGE_NAME=$REPOSITORY

		export NAME="$REGION-docker.pkg.dev/$PROJECT/$REPOSITORY/$IMAGE_NAME:$VERSION"

		docker build -t $NAME .
		docker run -p 8080:8080 $NAME
		```
* When Docker is done building the image, you can test it by opening a new terminal window and running:
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
* Once you get the output, you can go back to the terminal running the container and press `Ctrl+C` to stop the container.
* To push the Docker image to the Google Cloud Artifact Registry, run:
    * Command Prompt (Windows)
		```cmd
    	docker push %NAME%
    	```
    * Bash
		```bash
		docker push $NAME
		```

## Creating the Cloud Run service

* Go to [***Google Cloud Run***](https://console.cloud.google.com/run).
* Create a new service.
* Select the uploaded container image.
* Name the service.
* Choose a region.
* Choose `Require authentication` if you want to restrict the service to only be accessed by you and your other Google Cloud services.
* Under `Container, Networking, Security` in the `Container` section, set the memory capacity and CPU count according to the LLaMA model.
* Create the service.

## Testing the deployment

* To get the url of the Google Cloud Run service, run:
    * Command Prompt (Windows)
		```cmd
    	gcloud run services describe "Cloud Run service name" --region "Cloud Run service region" --format "value(status.url)" > temp.txt
    	SET /p URL= < temp.txt
    	DEL temp.txt
    	```
    * Bash
		```bash
		export URL=$(gcloud run services describe "Cloud Run service name" --region "Cloud Run service region" --format "value(status.url)")
		```
* To test the deployment on a Google Cloud Run service:
	* Which **does not** require any authentication, run:
    	* Command Prompt (Windows)
			```cmd
    		curl -X POST "%URL%/api/chat" ^
    		-H  "accept: application/json" ^
    		-H  "Content-Type: application/json" ^
    		-d "{\"messages\":[{\"role\":\"system\",\"content\":\"You are a helpful assistant AI.\"},{\"role\":\"user\",	\"content\":\"Who made Linux?\"}]}"
    		```
    	* Bash
			```bash
			curl -X POST "$URL/api/chat" \
			-H "accept: application/json" \
			-H "Content-Type: application/json" \
			-d "{\"messages\":[{\"role\":\"system\",\"content\":\"You are a helpful assistant AI.\"},{\"role\":\"user\",	\"content\":\"Who made Linux?\"}]}"	
			```
	* Which **has `Require authentication` enabled** for authentication:
    	* Command Prompt (Windows)
			```cmd
    		gcloud auth print-identity-token > temp.txt
    		SET /p ACCESS_TOKEN= < temp.txt
    		DEL temp.txt
			
    		curl -X POST "%URL%/api/chat" ^
    		-H  "accept: application/json" ^
    		-H  "Content-Type: application/json" ^
    		-H "Authorization: Bearer %ACCESS_TOKEN%" ^
    		-d "{\"messages\":[{\"role\":\"system\",\"content\":\"You are a helpful assistant AI.\"},{\"role\":\"user\",\"content\":\"Who made Linux?\"}]}"
			```
    	* Bash
			```bash
			export ACCESS_TOKEN=$(gcloud auth print-identity-token)
			
			curl -X POST "$URL/api/chat" \
    	    -H  "accept: application/json" \
    	    -H  "Content-Type: application/json" \
    	    -H "Authorization: Bearer $ACCESS_TOKEN" \
    	    -d "{\"messages\":[{\"role\":\"system\",\"content\":\"You are a helpful assistant AI.\"},{\"role\":\"user\",\"content\":\"Who made Linux?\"}]}"
			```
	* Which **uses Firebase Admin SDK** authentication:<br/>
		Your app or website will have to send a web request to the service. The URL to send the request to is the one you got from the previous step, the headers
		are `accept: application/json`, `Content-Type: application/json` and `Authorization: Bearer ID_TOKEN_GOES_HERE`. Remember to replace `ID_TOKEN_GOES_HERE` in
		the third header with the user's actual ID token. To retrieve the ID token, check out the [***Firebase documentation***](https://firebase.google.com/docs/auth/admin/verify-id-tokens#retrieve_id_tokens_on_clients). The data to send to the service should look something like this: `{"messages":[{"role":"system","content":"A system prompt for the AI"},{"role":"user","content":"A user's prompt for the AI."}]}`.
	* Which uses both **Firebase Admin SDK and has `Require authentication` enabled** for authentication:
		You will have to combine the method for testing the Admin SDK authentication and the one for testing the `Require authentication` option.

## Congrats!

You've deployed a `LLaMA` model to your Google Cloud Project!