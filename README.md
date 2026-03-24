# Example Home Assistant app repository

This repository can be used as a "blueprint" for app development to help you get started.

Apps documentation: <https://developers.home-assistant.io/docs/apps>

[![Open your Home Assistant instance and show the app store with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_store.svg)](https://my.home-assistant.io/redirect/supervisor_store/?repository_url=https%3A%2F%2Fgithub.com%2Fhome-assistant%2Fapps-example)

## Apps

This repository contains the following apps

### [Example app](./example)

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]

_Example app to use as a blueprint for new apps._

<!--

Notes to developers after forking or using the github template feature:
- While developing comment out the 'image' key from 'example/config.yaml' to make the supervisor build the app locally.
  - Remember to put this back when pushing up your changes.
- When you merge to the 'main' branch of your repository a new build will be triggered.
  - Make sure you adjust the 'version' key in 'example/config.yaml' when you do that.
  - Make sure you update 'example/CHANGELOG.md' when you do that.
  - The first time this runs you might need to adjust the image configuration on github container registry to make it public.
  - You may also need to adjust the GitHub Actions configuration (Settings > Actions > General > Workflow > Read & Write).
- Update the repository check in '.github/workflows/build-app.yaml' to match your repository name
  (the 'github.repository' condition in the 'prepare' job).
- Adjust the 'image' key in 'example/config.yaml' so it points to your username instead of 'home-assistant'
  (e.g., 'ghcr.io/my-username/my-app').
- Rename the example directory.
  - The 'slug' key in 'example/config.yaml' should match the directory name.
- Adjust all keys/urls that point to 'home-assistant' to now point to your user/fork.
- Share your repository on the forums https://community.home-assistant.io/c/projects/9
- Do awesome stuff!
 -->

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
