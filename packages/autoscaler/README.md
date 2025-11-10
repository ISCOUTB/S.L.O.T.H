# ETL Design Autoscaler

A containerized service for automatic scaling of Docker Swarm services, designed for the ETL Design ecosystem. The autoscaler monitors resource usage and adjusts the number of replicas for each service based on real-time metrics.

## Features

- Automatic scaling of Docker Swarm services based on CPU or memory usage.
- Prometheus integration for metrics collection.
- Flexible configuration via Docker labels and environment variables.
- Cooldown and check intervals to avoid rapid scaling.
- Stack-aware: can be limited to a specific Docker stack.

## Requirements

- **Docker Swarm**: The autoscaler manages services in a Swarm cluster.
- **Prometheus**: The autoscaler queries Prometheus for resource metrics.

Make sure Prometheus is running and scraping metrics from your Docker nodes (e.g., via cAdvisor).

## Configuration

### Environment Variables

- ```PROMETHEUS_URL``` (required): URL of your Prometheus server (e.g., <http://prometheus:9090/>).
- ```STACK_NAME``` (required): Name of the Docker stack to manage.
- ```CHECK_INVERVAL```: How often to check services (seconds, default: 30).
- ```COOLDOWN_PERIOD```: Minimum seconds between scaling actions for a service (default: 180).
- ```DEFAULT_MIN_REPLICAS```: Default minimum replicas if not set via label (default: 1).
- ```DEFAULT_MAX_REPLICAS```: Default maximum replicas if not set via label (default: 10).
- ```DEBUG```: Set to true for debug logging.

### Service Labels

Add these labels to your Docker services to enable autoscaling:

- ```scaler.enabled=true``` (required): Enable autoscaling for this service.
- ```scaler.min```: Minimum number of replicas.
- ```scaler.max```: Maximum number of replicas (-1, on-demand, or unlimited for no limit).
- ```scaler.metric```: Metric to use (cpu or memory).
- ```scaler.up```: CPU/memory percentage to scale up (default: 75).
- ```scaler.down```: CPU/memory percentage to scale down (default: 25).
- ```scaler.query```: (optional) Custom Prometheus query for advanced scenarios.

---

### Example Usage

```bash
docker run \
  -e PROMETHEUS_URL=http://prometheus:9090/ \
  -e STACK_NAME=my-stack \
  -e DEBUG=true \
  vulcan99/autoscaler:latest
```

### Example Service Definition

```yml
services:
  myservice:
    image: myimage:latest
    deploy:
      replicas: 2
      labels:
        - scaler.enabled=true
        - scaler.min=1
        - scaler.max=5
        - scaler.metric=cpu
        - scaler.up=80
        - scaler.down=30
```

> ⚠️ **Warning**  
> Make sure Prometheus is scraping metrics from your Docker nodes (e.g., using cAdvisor).  
> The autoscaler only manages services with the `scaler.enabled=true` label and matching `STACK_NAME`.  
> For advanced scenarios, use the `scaler.query` label to provide a custom Prometheus query.
