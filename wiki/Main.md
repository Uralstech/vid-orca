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
> I am using **llama-2-13b-chat.ggmlv3.q3_K_S.bin** from https://huggingface.co/TheBloke/ converted to GGUF (it is available here: <https://huggingface.co/uralstech/LLaMA-2-13b-Chat-GGUF>).
> I am using the 13b model as it has good performance at much lower hardware requirements than the 70b model.

* Move the downloaded `.bin` file to the **models** folder.

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

## Changelog
* v1.2.10 **[Breaking changes]**
	* Updated to LLaMA CPP Python v0.1.81.
		- **GGML models *will not* work, as LLaMA CPP has dropped GGML support.**
		- I am working on a tutorial on how to convert your GGML models to GGUF models.
		- Currently, I am using a converted GGUF model of the original 13b model I was previously using. You can find it here: <https://huggingface.co/uralstech/LLaMA-2-13b-Chat-GGUF>
	* Firebase Admin SDK authentication will now work on Google Compute Engine Virtual Machines.
	* All scripts should now work with earlier versions of Python.
		- Tested on Python 3.8.10.