# isat-cv

## About

isat-cv is an educational project for ISaT and CV courses in Saratov State
University.

<!--- Add more info about project -->

## Prerequisites
* Python
* Docker
* [`just`](https://github.com/casey/just) (optional)

<!--- Correct grammar here -->

## Usage

1. Copy `config/example.json` to `config/config.json` and set needed config 
values.
2. If `just` is installed, run `just init && just start`, otherwise, copy
commands from `justfile` and run them manually.
3. To run frontend part, change directory to `frontend` and run `npm i`, then
`npm run dev -- --start`.
