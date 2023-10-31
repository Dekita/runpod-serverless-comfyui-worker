
## Use Github Actions to Automatically deploy to Docker Hub 
The repo contains two workflows that publishes the image to Docker hub using Github Actions:
* [docker-dev.yml](.github/workflows/docker-dev.yml): Creates the image and pushes it to Docker hub with the `dev` tag on every push to the `main` branch
* [docker-release.yml](.github/workflows/docker-release.yml): Creates the image and pushes it to Docker hub with the `latest` and the release tag. It will only be triggered when you create a release on GitHub

If you want to use this, you should add these secrets to your repository:

| Configuration Variable | Description                                                  | Example Value         |
| ---------------------- | ------------------------------------------------------------ | --------------------- |
| `DOCKERHUB_USERNAME`   | Your Docker Hub username.                                    | `your-username`       |
| `DOCKERHUB_TOKEN`      | Your Docker Hub token for authentication.                    | `your-token`          |
| `DOCKERHUB_REPO`       | The repository on Docker Hub where the image will be pushed. | `timpietruskyblibla`  |
| `DOCKERHUB_IMG`        | The name of the image to be pushed to Docker Hub.            | `runpod-worker-comfy` |
