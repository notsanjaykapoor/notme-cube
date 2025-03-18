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

#### Distributed Queues

I have encountered the following problem a few times - you have a very dynamic workload that varies greatly during the day and want distributed queues to handle those peak workloads efficiently.  Kubernetes and Kafka are really incredible tools and I have used them often.  I have also seen some pretty decent size cloud bills.  

This distributed queue solution uses lower cost vps providers with well documented api's (e.g. Digital Ocean, Hetzner), an open source networking infrastructure called Nats, and Postgres as a job queue to implement a solution that can distribute workloads across multiple machines and auto scale up/down those machines as required.

Each cluster is a group of machines, which are scaled up/down as necessary:

![Machine Scaling Example](https://ik.imagekit.io/notme001/readme/notme_cluster_scaling.png "machine scaling example")

![Machine Scaled Example](https://ik.imagekit.io/notme001/readme/notme_cluster_scaled.png "machine scaled example")

As a machine comes up, it joins the work group dynamically and is available to process jobs:

![Work Queue Example](https://ik.imagekit.io/notme001/readme/notme_cluster_workq_1.png "work queue example")


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


