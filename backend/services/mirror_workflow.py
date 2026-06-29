"""Gitea Actions workflow generation for mirrored repos."""

from .mirror_models import MirrorConfig


def generate_workflow(config: MirrorConfig) -> str:
    """Generate a Gitea Actions deploy workflow file for a mirror config."""
    if config.docker_image:
        return f"""name: Deploy

on:
  push:
    branches:
      - {config.deploy_branch}

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Build Docker image
        run: |
          docker build -t {config.docker_image} .

      - name: Push to registry
        run: |
          echo "Push to registry here"

      - name: Deploy
        run: |
          echo "Deploy application"
"""
    return f"""name: Deploy

on:
  push:
    branches:
      - {config.deploy_branch}

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Deploy
        run: |
          echo "Deploy application"
"""
