# Vid Orca
Deploy LLaMA Chat on Google Cloud Run.

## What you will need
* [***Docker Desktop***](https://www.docker.com/)
* [***Google Cloud CLI***](https://cloud.google.com/sdk/docs/install)

## Setup
* Fork/Download this repo and create a new folder called `models`.
* Download any **LLaMA-derived** LLM (I used `orca-mini-7b.ggmlv3.q4_0.bin` from https://gpt4all.io/index.html, hence the project name).
* Rename the file to `model.bin`
* Move `model.bin` to the `models` folder.
* For new projects:
    * Go to [***Google Cloud Console***](https://console.cloud.google.com/) and create a new project.
    * Link a billing account to the project.
* Enable the needed services:
    ```cmd
    REM All commands you will see in this tutorial are for Command Prompt on Windows.
    gcloud services enable artifactregistry.googleapis.com run.googleapis.com
    ```
* Go to the [***Google Cloud Artifact Registry***](https://console.cloud.google.com/artifacts) for your project and create a new repository.
* Name your repository.
* Make sure the format is `Docker`.
* Choose a region or multi-region area.
* Create your repository.
* Set up authentication for Docker as described in the [***Google Cloud Artifact Registry documentation***](https://cloud.google.com/artifact-registry/docs/docker/authentication).

## Building and testing the Docker image
* Replace `REGION`, `PROJECT`, `REPOSITORY` and `IMAGE_NAME` with your desired values an run:
    ```cmd
    SET VERSION="1.1.0"
    SET REGION="Google Cloud Platform region"
    SET PROJECT="Google Cloud project ID"
    SET REPOSITORY="Google Cloud Artifact Registry repository name"

    REM The below line will make the image name the same as the repository name. To change this replace %REPOSITORY% with the name.
    SET IMAGE_NAME=%REPOSITORY%

    SET NAME="%REGION%-docker.pkg.dev/%PROJECT%/%REPOSITORY%/%IMAGE_NAME%-v%VERSION%"

    docker build -t %NAME% .
    docker run -p 8080:8080 %NAME%
    ```
* If there are no errors and Docker is done building the image, open a new terminal window and run:
    ```cmd
    curl -X POST "http://localhost:8080/api/chat" ^
    -H  "accept: application/json" ^
    -H  "Content-Type: application/json" ^
    -d "{\"messages\":[{\"role\":\"system\",\"content\":\"You are a helpful assistant AI.\"},{\"role\":\"user\",\"content\":\"Who made Linux?\"}]}"
    ```
* If there are no errors and you get an output, you can go back to the terminal running the container and press `Ctrl+C` to stop the container.

## Pushing the image to the Google Cloud Artifact Registry and deploying it to Google Cloud Run
* To push the Docker image to the Google Cloud Artifact Registry, run:
    ```cmd
    docker push %NAME%
    ```
* Go to [***Google Cloud Run***](https://console.cloud.google.com/run).
* Create a new service.
* Select the uploaded container image.
* Name the service.
* Choose a region.
* Choose `Require authentication` if needed.
* Under `Container, Networking, Security` in the `Container` section, set the memory capacity and CPU count according to the LLaMA model.
* Create the service.

## Testing the deployment
* To get the url of the Google Cloud Run service, run:
    ```cmd
    gcloud run services describe "Cloud Run service name" --region "Cloud Run service region" --format "value(status.url)" > temp.txt
    SET /p URL= < temp.txt
    DEL temp.txt
    ```

* To test the deployment on a Google Cloud Run service which **does not** require authentication, run:
    ```cmd
    curl -X POST "%URL%/api/chat" ^
    -H  "accept: application/json" ^
    -H  "Content-Type: application/json" ^
    -d "{\"messages\":[{\"role\":\"system\",\"content\":\"You are a helpful assistant AI.\"},{\"role\":\"user\",\"content\":\"Who made Linux?\"}]}"
    ```
* To test the deployment on a Google Cloud Run service which **does** require authentication, run:
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

## Congrats!
You've deployed a `LLaMA` model to your Google Cloud Project!

## License
The license and notice for the code in the repository can be found here: (https://github.com/Uralstech/Vid-Orca/blob/main/LICENSE) and here: (https://github.com/Uralstech/Vid-Orca/blob/main/NOTICE) respectively.