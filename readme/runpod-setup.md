## RunPod worker setup guide

### Template Setup: 
* Create a [new template](https://runpod.io/console/serverless/user/templates) by clicking on `New Template` 
* In the dialog, configure:
  * Template Name: `runpod-serverless-comfyui-worker` (can be anything you want)
  * Container Image: `<dockerhub_username>/<repository_name>:tag`, in this case: `dekita/runpod-serverless-comfyui-worker:latest` (or `dev` if you want dev release)
  * Container Registry Credentials: Add you dockerhub credentials here. You can leave everything as it is if using this public repo,
  * Container Disk: `25 GB`
  * Enviroment Variables: [Configure ENV](/readme/env-setup.md)
    * Note: You can also not configure it, the images will then stay in the worker. 
* Click on `Save Template`

### Endpoint Setup: 
* Navigate to [`Serverless > Endpoints`](https://www.runpod.io/console/serverless/user/endpoints) and click on `New Endpoint`
* In the dialog, configure:
  * Endpoint Name: `comfy` (can be anything you want)
  * Select Template: `runpod-comfy-worker` (or what ever name you gave your template)
  * Active Workers: `0` (what ever makes sense for you, 1+ will ensure workers are always running/billing you)
  * Max Workers: `3` (what ever makes sense for you)
  * Idle Timeout: `5` (you can leave the default)
  * Flash Boot: `enabled` (doesn't cost more, but provides faster boot of our worker, which is good)
  * Advanced: Leave the defaults (or set network volume is desired)
  * Select a GPU that has some availability
  * GPUs/Worker: `1`
* Click `deploy`
After your endpoint is created you can click on it to see the dashboard and view logs, 
Once the endpoint workers have finished pulling your selected templates docker image, you can trigger calls to the runpod endpoint to begin generating the most awesome artworks!

### Volume Setup: 
- todo :sadface:
