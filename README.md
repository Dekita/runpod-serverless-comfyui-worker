<p align="center"><img src="assets/runpod-worker-logo.webp" title="Runpod Worker Thread" /></p>

# runpod-comfyui-worker
A somewhat optimized, serverless [ComfyUI](https://github.com/comfyanonymous/ComfyUI) worker for [RunPod](https://www.runpod.io/), highly specific to my own personal use case, which just happens to require a lot of customization and flexibility! :heart:


## Features 
* Launch [ComfyUI](https://github.com/comfyanonymous/ComfyUI) workflows on demand in seconds
* Automatically upload generations to Amazon AWS *(requires [ENV Variables](/readme/aws-setup.md))
* Image based on [Ubuntu + NVIDIA CUDA](https://hub.docker.com/r/nvidia/cuda)
* Sends progress updates so you can track/display them in your own ui
* Easily add custom models/loras/nodes/etc via a selection of methods
* Returning base64 data for generated images *(when not aws && tobase64 flag set)
* Allows for batch image processing && bulk AWS uploads
* Job output also returns non image/video node outputs 


## Default models/nodes for dekita/runpod-comfyui-worker:latest
* model: [sd_xl_base_1.0.safetensors](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0)
* model: [sdxl_vae.safetensors](https://huggingface.co/stabilityai/sdxl-vae/)
* nodes: [efficiency-nodes-comfyui](https://github.com/LucianoCirino/efficiency-nodes-comfyui)
* nodes: [comfyui-wd14-tagger](https://github.com/pythongosssss/ComfyUI-WD14-Tagger)


## Runpod.io Quickstart 
* 🐳 Use the latest image for your worker: [dekita/runpod-comfyui-worker:latest](https://hub.docker.com/r/dekita/runpod-comfyui-worker)
* ⚙️ [Setup environment variables for AWS](/readme/aws-setup.md)
* ℹ️ [Use the Docker image on RunPod](/readme/runpod-setup.md)


## Detailed Guides
* [Building Customized Image](/readme/custom-image.md) (optional)
* [Setup Amazon AWS S3](/readme/aws-setup.md) (optional)
* [Get the workflow from ComfyUI](/readme/get-workflow.md) 
* [Interact with your RunPod API](/readme/api-interactions.md) 
* [Github Actions: Auto Deploy to Docker Hub](/readme/auto-deploy.md) (optional)


## Additional Acknowledgements
* This project was initially a fork of: [runpod-worker-comfy](https://github.com/blib-la/runpod-worker-comfy). Huge credit to [Tim Pietrusky](https://github.com/TimPietrusky), the initial contributor of that project!
* Thanks to [comfyanonymous](https://github.com/comfyanonymous) for creating [ComfyUI](https://github.com/comfyanonymous/ComfyUI), which provides such an awesome API to interact with Stable Diffusion!
