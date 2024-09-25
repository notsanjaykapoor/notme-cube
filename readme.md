#### Install

This repo uses [uv](https://docs.astral.sh/uv/) as its package manager:

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Create a virtual environment using a specific python version:

```
uv venv --python <path/to/python>
```

Install project dependencies:

```
uv sync
```


#### Dev

The dev environment uses a env file to define its environment:

```
cp env.example .env # define your env vars
```

Start the dev server:

```
make dev
```


#### Build

```
make build
```


#### Deploy

The deploy process assumes the app will run on a vps and be accessible via a cloudflare tunnel.  This process requires 2 separate environment files:

- .env.vps # defines deploy specific env vars
- .env.your-app-name # defines app specific env vars


The deploy process will:

- download the image to the vps
- start/re-start the app on a defined port

```
make deploy
```

The cloudflare tunnel will be the app's reverse proxy and is configured using the [cloudflare dashboard](https://dash.cloudflare.com/).


