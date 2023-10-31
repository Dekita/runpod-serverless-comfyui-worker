## Configuring Models / Nodes for your custom image
Edit `custom/custom-files.json` to include any custom files you wish to download at build time. This allows for you to easily define any custom nodes, models, loras, upscalers, etc. Any valid downloadable file can included this way, including models, git repos, and more! 

### Restrictions & Limitations
If your runpod worker image is too large, you will find that your workers spend a LOT of time throttled, typically caused by redownloading the image from cache to keep the worker fresh. As desirable as it might be to include all your favourite models directly in the built image, this is NOT RECOMMENDED!!

The best approach, assuming you want incredibly fast image build/upload/download times, is to only include absolutely required files in your final image, and then have all additional models/loras/etc loaded by [Network Volume](/readme/network-volume.md). HOWEVER, this is NOT as fast as loading models directly from the container image. 

### Format for custom/custom-files.json
The json file should contain an array of objects in the format detailed below:
```json
[
    {
        "url": "https://some.url/filename.git",
        "path": "custom_nodes/filename"
    },
    {
        "url": "https://some.url/model",
        "path": "models/filename.ckpt"
    }
]
```

### Custom Models

#### Base SD1.5 (4.27GB) + Additional VAE (335MB)
```json
[
    {
        "url": "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors",
        "path": "models/checkpoints/v1-5-pruned-emaonly.safetensors"
    },
    {
        "url": "https://huggingface.co/stabilityai/sd-vae-ft-mse-original/resolve/main/vae-ft-mse-840000-ema-pruned.safetensors",
        "path": "models/vae/vae-ft-mse-840000-ema-pruned.safetensors"
    }
]
```

#### Base SDXL (6.94GB) + Refiner (6.08GB) + Offset Lora (50MB) + VAE (335MB)
```json
[
    {
        "url": "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors",
        "path": "models/checkpoints/sd_xl_base_1.0.safetensors"
    },
    {
        "url": "https://huggingface.co/ckpt/sd_xl_refiner_1.0/resolve/main/sd_xl_refiner_1.0.safetensors",
        "path": "models/checkpoints/sd_xl_refiner_1.0.safetensors"
    },
    {
        "url": "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_offset_example-lora_1.0.safetensors",
        "path": "models/loras/sd_xl_offset_lora_1.0.safetensors"
    },
    {
        "url": "https://huggingface.co/madebyollin/sdxl-vae-fp16-fix/resolve/main/sdxl_vae.safetensors",
        "path": "models/vae/sdxl_vae.safetensors"
    }
]
```

### Custom Nodes
Below is a selection of custom-file configurations for specific purposes. Simply include the relevant objects within your own custom-files.json file. 

#### Efficiency-Nodes-ComfyUI (285MB)
This configuration will download the latest comfyui efficiency nodes from github, along with the models required to use it. If required models arent downloaded now, they will be at runtime - we DONT want that!!
```json
[
    {
        "url": "https://github.com/LucianoCirino/efficiency-nodes-comfyui.git",
        "path": "custom_nodes/efficiency-nodes-comfyui"
    }
]
```


#### SDXL-Prompt-Styler (2MB)
This configuration will download the latest sdxl-prompt-styler node from github. Additional models not required for this node. 
```json
[
    {
        "url": "https://github.com/twri/sdxl_prompt_styler.git",
        "path": "custom_nodes/sdxl_prompt_styler"
    }
]
```


#### ComfyQR (28MB) + QR Code Monster (689MB)
This configuration will download [ComfyQR](https://github.com/coreyryanhanson/ComfyQR) nodes and the [QR Code Monster](https://civitai.com/models/111006?modelVersionId=122143) controlnet to generate qr images!
```json
[
    {
        "url": "https://github.com/coreyryanhanson/ComfyQR.git",
        "path": "custom_nodes/ComfyQR"
    },
    {
        "url": "https://civitai.com/api/download/models/122143",
        "path": "models/controlnet/qrCodeMonster_v20.safetensors"
    }
]
```


#### ComfyUI-WD14-Tagger
This configuration will download the latest wd14-tagger node from github, along with the models required to use it. If required models arent downloaded now, they will be at runtime - we DONT want that!! Utilizing this node on generated images will scan them for danboru tags and return that information with the job output. 
```json
[
    {
        "url": "https://github.com/pythongosssss/ComfyUI-WD14-Tagger.git",
        "path": "custom_nodes/ComfyUI-wd14-tagger"
    },
    {
        "url": "TODO",
        "path": "MODELS..."
    },
    {
        "url": "TODO",
        "path": "MODELS..."
    }
]
```

#### AnimateDiff + VHS
This configuration will download a number of custom nodes from github alongside motion modules for animatediff. Animatediff is used to enable gif/mp4 video generations!! 
```json
[
    {
        "url": "TODO",
        "path": "TODO"
    }
]
```

