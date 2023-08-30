# Vid Orca

## NOTE
This is still incomplete! I am working on finishing the wiki.

## Deploying LLaMA models to Google Cloud

### What you will need

* [***Docker Desktop***](https://www.docker.com/)
* [***Google Cloud CLI***](https://cloud.google.com/sdk/docs/install)

### Basic setup
* Fork/Download this repo and create a new folder called **models**.
* Download any **LLaMA or LLaMA 2 derived GGUF model**.
	
	> With LLaMA CPP dropping support for GGML models, you will have to convert your GGML models to GGUF using the scripts given in the LLaMA CPP repo.<br/>
	> I am working on a tutorial on how to do so. But here are the basic steps on how to do it:
	>  * Clone the [***LLaMA CPP repo***](https://github.com/ggerganov/llama.cpp).
	>  * Follow the installation steps given [***here***](https://github.com/ggerganov/llama.cpp#build). 
	>  * Run `pip install -r requirements.txt`.
	>  * For LLaMA 2 models, run:<br/>
	>	  `python convert-llama-ggmlv3-to-gguf.py --input PATH_TO_THE_INPUT_GGML_FILE --output PATH_TO_THE_OUTPUT_GGUF_FILE --name "NAME OF YOUR MODEL" --eps 1e-5 --context-length 4096`
	>  * For LLaMA 1 models, run:<br/>
	>	  `python convert-llama-ggmlv3-to-gguf.py --input PATH_TO_THE_INPUT_GGML_FILE --output PATH_TO_THE_OUTPUT_GGUF_FILE --name "NAME OF YOUR MODEL" --eps 1e-6 --context-length 2048`
	>  > For my LLaMA 2 13b model, on Linux, the command is:<br/>
	>  >  `python3 convert-llama-ggmlv3-to-gguf.py --input ../vid-orca/NOCOMMIT/Models/llama-2-13b-chat.ggmlv3.q3_K_S.bin --output ../vid-orca/models/llama-2-13b-chat.gguf.q3_K_S.bin --name "LLaMA-2 13b GGUF q3_K_S" --eps 1e-5 --context-length 4096`
	>
	> You've now converted your GGML model to a GGUF model! Just a few things to note about the commands above:
	>  * You may need to replace `pip` and/or `python` with `pip3` and/or `python3`, depending on your Python configuration.
	>  * If your LLaMA 1 models have a context length of more than 2048 or your LLaMA 2 models have it more than 4096, you will have to increase the `--context-length` argument of the conversion command. 
	> <br/><br/>
	>
	> I am using **llama-2-13b-chat.ggmlv3.q3_K_S.bin** from <https://huggingface.co/TheBloke/Llama-2-13B-chat-GGML> converted to GGUF (it is available here: <https://huggingface.co/uralstech/LLaMA-2-13b-Chat-GGUF>).
	> I am using the 13b model as it has good performance at much lower hardware requirements than the 70b model.

* Move the downloaded `.bin` file to the **models** folder.
* In the `main.py` file, under the `src` folder, change the following lines:
	* Change the last part of the `MODEL_PATH` variable (line **18**) to your model file's name. Like `../models/Your-LLaMA-2_model.bin`.
	* Add your model's name to the `APP_NAME` variable (line **21**).

### Authentication
Depending on your use, you may or may not need client authentication for the Cloud Run/Compute Engine service.
If you are making an app which uses the service, for example, you may want authentication so that only your app's users can access it.

This project is configured to use Firebase Admin SDK authentication, so, if you already have Firebase Auth set up in your app, you can integrate the service easily.

If you **do not** want authentication or are using a different method of authenticating your users, here are the steps to remove the Admin SDK integration from Vid Orca:
* In `main.py`, set the `USE_FIREBASE_ADMIN_AUTH` variable (line **16**) to `False`.
* In `Dockerfile` remove line **37**

If you **want** end-user authentication for the service using Firebase Admin SDK,
link a [***Firebase***](https://console.firebase.google.com/) project to your Google Cloud project, if you haven't already.<br/>
Your app or website will also need [***Firebase Authentication***](https://firebase.google.com/docs/auth/where-to-start) to be able to access the service.

If you are using Google Cloud Run (more about that later), there is also a way to restrict access to only you and other Google Cloud services.  

### Google Cloud project setup
* For new Google Cloud projects:
    * Go to [***Google Cloud Console***](https://console.cloud.google.com/) and create a new project.
    * Link a billing account to the project.
* Enable the Artifact Registry API:
    ```bash
    gcloud services enable artifactregistry.googleapis.com
    ```

### Google Cloud Artifact Registry setup

* Go to the [***Google Cloud Artifact Registry***](https://console.cloud.google.com/artifacts) for your project and create a new repository.
* Name your repository.
* Set the format to `Docker`.
* Choose a region or multi-region area.
* Create your repository.
* Set up authentication for Docker using one of the ways defined in the [***Google Cloud Artifact Registry documentation***](https://cloud.google.com/artifact-registry/docs/docker/authentication).

### Choose your path
I have documented two ways of deploying LLaMA models to Google Cloud. Choose what is best for you!

#### Using Google Cloud Run

* **Pros**
	* **Easy to setup.**
	* **Very cheap.** Google only charges you while a request is being processed (depending on your setup).
* **Cons**
	* **Very slow.** Cloud Run does not allow you to use GPUs.
		* My 13b model took nearly **two minutes** to process a single request.

If you want to deploy your model to Google Cloud Run, check out <https://github.com/uralstech/vid-orca/wiki/Google-Cloud-Run>.

#### Using Google Compute Engine VMs

* **Pros**
	* **GCE allows you to use GPUs.** This makes your models ***way*** faster.
		* My 13b model only took **ten seconds** to process a request.
* **Cons**
	* **Harder to set up.**
	* **More expensive than Cloud Run and charges you for the whole time the VM is running.** In my configuration, it costs **$0.34 per *hour*** or **$228.93 per *month***.

If you want to deploy your model to Google Compute Engine, check out <https://github.com/uralstech/vid-orca/wiki/Google-Compute-Engine>.

## Changelog
* v1.2.10 **[Breaking changes]**
	* Updated to LLaMA CPP Python v0.1.81.
		- **GGML models *will not* work, as LLaMA CPP has dropped GGML support.**
		- I am working on a tutorial on how to convert your GGML models to GGUF models.
		- Currently, I am using a converted GGUF model of the original 13b model I was previously using. You can find it here: <https://huggingface.co/uralstech/LLaMA-2-13b-Chat-GGUF>
	* Firebase Admin SDK authentication will now work on Google Compute Engine Virtual Machines.
	* All scripts should now work with earlier versions of Python.
		- Tested on Python 3.8.10.