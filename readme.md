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
cp env.example .env
```

Define your environment in .env, and then start the dev server:

```
make dev
```

#### Password Manager

The password interface uses the [pass](https://www.passwordstore.org/) tool to store passwords in gpg encrypted files.  The password user interface enables creating new passwords and showing existing passwords:

![Password List Example](https://ik.imagekit.io/notme001/readme/passw_list_example.png "passw list example")

![Password Show Example](https://ik.imagekit.io/notme001/readme/passw_show_example.png "passw show example")


#### Build

Build docker image:

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


