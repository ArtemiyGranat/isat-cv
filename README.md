# isat-cv

## About

isat-cv is an educational project for ISaT and CV courses in Saratov State
University.

## Prerequisites
* Python
* Docker
* [`just`](https://github.com/casey/just) (optional)

## Usage

1. Set needed config values in `config/config.json`, rename `.env.sample` in
root and `frontend` directory to `.env` and set environment variables.
2. If `just` is installed, run `just init && just start`, otherwise, copy
commands from `justfile` and run them manually.
3. To run only frontend part, `just start frontend`.
