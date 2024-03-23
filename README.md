# isat-cv

## About

isat-cv is an educational project for Intelligent Systems & Technologies and 
Computer Vision courses at Saratov State University.

## Features
1. Checking duplicates using perceptual hash
2. Removing background of images using database watchdog
3. Search for similar images
4. Image search by text query
5. Search for images with similar and complementary colors
6. Mix two images using Laplacian and Gaussian pyramids

## Prerequisites
* Python
* Docker
* [`just`](https://github.com/casey/just) (optional)

## Usage

1. Set the required configuration values to `config/config.json`, rename `.env.sample` in
root project and `frontend` directory to `.env` and set environment variables.
2. If `just` is installed, run `just init && just start`, otherwise, copy
commands from `justfile` and run them manually.
3. To run only frontend part, `just start frontend`.
