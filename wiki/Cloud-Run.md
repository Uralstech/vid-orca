# Deploying LLaMA models to Google Cloud Run

## Setup

### Basics

* Fork/Download this repo and create a new folder called **models**.
* Download any **LLaMA or LLaMA 2 derived GGML model which supports LLaMA CPP**. I used **orca-mini-7b.ggmlv3.q4_0.bin** from https://gpt4all.io/index.html originally, hence the project name. I am now using **llama-2-7b.ggmlv3.q4_K_S.bin** and **llama-2-13b-chat.ggmlv3.q3_K_S.bin** from https://huggingface.co/TheBloke/. For me, 13b yields the best results, as when using Google Cloud Run it's not possible to use any models requiring a GPU or more than 34 GBs of RAM, like LLaMA2 70b.
* Move the downloaded `.bin` file to the **models** folder.
* In **src/main.py**, line **16**, update `MODEL_PATH` with your model's filename.

### Google Cloud project

* For new Google Cloud projects:
    * Go to [***Google Cloud Console***](https://console.cloud.google.com/) and create a new project.
    * Link a billing account to the project.
* Enable the needed services:
    ```bash
    gcloud services enable artifactregistry.googleapis.com run.googleapis.com
    ```

### Google Cloud Artifact Registry

* Go to the [***Google Cloud Artifact Registry***](https://console.cloud.google.com/artifacts) for your project and create a new repository.
* Name your repository.
* Make sure the format is `Docker`.
* Choose a region or multi-region area.
* Create your repository.

### Google Cloud Artifact Registry authentication

* Set up authentication for Docker as described in the [***Google Cloud Artifact Registry documentation***](https://cloud.google.com/artifact-registry/docs/docker/authentication).

## Authentication for the Google Cloud Run service

* If you **do not want end-user authentication for the service *OR* only want other Google Cloud services and/or *you* to use it**:
	* Remove lines **6-9** in **requirements.txt**.
	* Change line **15** in **src/main.py** to `USE_FIREBASE_ADMIN_AUTH: bool = False`.
* If you ***want* end-user authentication for the service**, like if you want this to be used on your website or app:
	* Link a [***Firebase***](https://console.firebase.google.com/) project to your Google Cloud project.
	* Your app or website needs [***Firebase Authentication***](https://firebase.google.com/docs/auth/where-to-start) to be able to access the Google Cloud Run service.<br/>
	Note: A Firebase Admin SDK service account is required to communicate with Firebase. This service account is created automatically when you create a Firebase project or add Firebase to a Google Cloud project.

## Building and testing the Docker image

* Replace `REGION`, `PROJECT`, `REPOSITORY` and `IMAGE_NAME` with your desired values an run:<br/>
	Note: If you want to test/run this locally, you will **have** to set `USE_FIREBASE_ADMIN_AUTH` to `False`. Once you're ready to upload to Google Cloud Run, you can set it to `True` and build the Docker image again.
    * Command Prompt (Windows)
    	```cmd
    	SET VERSION="1.2.7"
    	SET REGION="Google Cloud Platform region"
    	SET PROJECT="Google Cloud project ID"
		SET REPOSITORY="Google Cloud Artifact Registry repository name"

		REM The below line will make the image name the same as the repository name. To change it, replace %REPOSITORY% with the name.
    	SET IMAGE_NAME=%REPOSITORY%

    	SET NAME="%REGION%-docker.pkg.dev/%PROJECT%/%REPOSITORY%/%IMAGE_NAME%-v%VERSION%"

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

		export NAME="$REGION-docker.pkg.dev/$PROJECT/$REPOSITORY/$IMAGE_NAME-v$VERSION"

		docker build -t $NAME .
		docker run -p 8080:8080 $NAME
		```
* If there are no errors and Docker is done building the image, open a new terminal window and run (again, this will only work if `USE_FIREBASE_ADMIN_AUTH` is `False`):
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
* If there are no errors and you get an output, you can go back to the terminal running the container and press `Ctrl+C` to stop the container.

## Pushing the image to the Google Cloud Artifact Registry and deploying it to Google Cloud Run

* To push the Docker image to the Google Cloud Artifact Registry, run:
    * Command Prompt (Windows)
		```cmd
    	docker push %NAME%
    	```
    * Bash
		```bash
		docker push $NAME
		```
* Go to [***Google Cloud Run***](https://console.cloud.google.com/run).
* Create a new service.
* Select the uploaded container image.
* Name the service.
* Choose a region.
* Choose `Require authentication` if you do not want the public to access the service. This will restrict it to only be accessed by you and your other Google Cloud services. This should not be enabled if you want Firebase Admin SDK authentication.
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

## Congrats!

You've deployed a `LLaMA` model to your Google Cloud Project!