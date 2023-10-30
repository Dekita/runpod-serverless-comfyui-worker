
## Build the image

You can build the image locally: `docker build -t timpietruskyblibla/runpod-worker-comfy:dev .`

## Local testing

* Make sure you have Python >= 3.10
* Install the dependencies: `pip install -r requirements.txt`
* Then you can run the handler: `python src/rp_handler.py`

If you want to run the Docker container, you can use: `docker-compose up`

Both will use the data from [test_input.json](./test_input.json).

### Test setup for Windows

**Note**: Our hope was that we can use this Docker Image with Docker Desktop on Windows. But regardless what we did, it was not possible. So we decided to use Ubuntu as part of WSL (Windows Subsystem for Linux) inside of Windows. This works without any problems, but only if you don't run Docker on Windows itself.

To run the Docker image on Windows, we need to have WSL2 and a Linux distro (like Ubuntu) installed on Windows.

- Follow the [guide on how to get WSL2 and Linux installed in Windows](https://ubuntu.com/tutorials/install-ubuntu-on-wsl2-on-windows-11-with-gui-support#1-overview) to install Ubuntu
  - You can skip the "Install and use a GUI package" part as we don't need a GUI

* When Ubuntu is installed, you have to login to Ubuntu in the terminal: `wsl -d Ubuntu`
* Update the packages: `sudo apt update`
* [Install Docker in Ubuntu](https://docs.docker.com/engine/install/ubuntu/) & then install docker-compose `sudo apt-get install docker-compose`
* [Install the NVIDIA Toolkit in Ubuntu](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#configuring-docker) and create the `nvidia` runtime

- [Enable GPU acceleration on Ubuntu on WSL2 to use NVIDIA CUDA](https://ubuntu.com/tutorials/enabling-gpu-acceleration-on-ubuntu-on-wsl2-with-the-nvidia-cuda-platform#1-overview)

  - For the step "Install the appropriate Windows vGPU driver for WSL": If you already have your GPU driver installed on Windows, you can skip this

- Add your user to the `docker` group, so that you can use Docker without `sudo`: `sudo usermod -aG docker $USER`


## Automatically deploy to Docker hub with Github Actions
Thanks to [runpod-worker-comfy](https://github.com/blib-la/runpod-worker-comfy), which this repo was initially based on, this repo contains two workflows that publish the image to Docker hub using Github Actions:

* [docker-dev.yml](.github/workflows/docker-dev.yml): Creates the image and pushes it to Docker hub with the `dev` tag on every push to the `main` branch
* [docker-release.yml](.github/workflows/docker-release.yml): Creates the image and pushes it to Docker hub with the `latest` and the release tag. It will only be triggered when you create a release on GitHub

If you want to use this, you should add these secrets to your repository:

| Configuration Variable | Description                                                  | Example Value         |
| ---------------------- | ------------------------------------------------------------ | --------------------- |
| `DOCKERHUB_USERNAME`   | Your Docker Hub username.                                    | `your-username`       |
| `DOCKERHUB_TOKEN`      | Your Docker Hub token for authentication.                    | `your-token`          |
| `DOCKERHUB_REPO`       | The repository on Docker Hub where the image will be pushed. | `timpietruskyblibla`  |
| `DOCKERHUB_IMG`        | The name of the image to be pushed to Docker Hub.            | `runpod-worker-comfy` |
