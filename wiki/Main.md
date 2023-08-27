# Vid Orca

## NOTE
This is still incomplete! I am working on finishing the wiki.

## Changelog
* v1.2.10 **[Breaking changes]**
	* Updated to LLaMA CPP Python v0.1.81.
		- **GGML models *will not* work, as LLaMA CPP has dropped GGML support.**
		- I am working on a tutorial on how to convert your GGML models to GGUF models.
		- Currently, I am using a converted GGUF model of the original 13b model I was previously using. You can find it here: <https://huggingface.co/uralstech/LLaMA-2-13b-Chat-GGUF>
	* Firebase Admin SDK authentication will now work on Google Compute Engine Virtual Machines.
	* All scripts should now work with earlier versions of Python.
		- Tested on Python 3.8.10.
	

## Deploying LLaMA models to Google Cloud

### What you will need

* [***Docker Desktop***](https://www.docker.com/)
* [***Google Cloud CLI***](https://cloud.google.com/sdk/docs/install)

### Choose your path
I have documented two ways of deploying LLaMA models to Google Cloud. Choose what is best for you!

#### Using Google Cloud Run

* **Pros**
	* **Easy to setup.**
	* **Very cheap.** Google only charges you while a request is being processed (depending on your setup).
* **Cons**
	* **Very slow.** Cloud Run does not allow you to use GPUs.
		* My 13b model took nearly **two minutes** to process a single request.

#### Using Google Compute Engine VMs

* **Pros**
	* **GCE allows you to use GPUs.** This makes your models ***way*** faster.
		* My 13b model only took **ten seconds** to process a request.
* **Cons**
	* **Harder to set up.**
	* **More expensive than Cloud Run and charges you for the whole time the VM is running.** In my configuration, it costs **$0.34 per *hour*** or **$228.93 per *month***.
