# Tyrell K8s - Service Access

POC credentials for all services. **Internal network only** - not internet exposed.

## HTTP Services (via Envoy Gateway)

| Service | URL | Username | Password |
|---------|-----|----------|----------|
| Grafana | <http://grafana.k8s.tyrell.com.au> | `admin` | `<REDACTED-SEE-VAULT>` |
| Prometheus | <http://prometheus.k8s.tyrell.com.au> | - | - |
| Kafbat UI | <http://kafka.k8s.tyrell.com.au> | - | - |
| MinIO Console | <http://minio.k8s.tyrell.com.au> | `admin` | `<REDACTED-SEE-VAULT>` |
| MinIO S3 API | <http://s3.k8s.tyrell.com.au> | `admin` | `<REDACTED-SEE-VAULT>` |
| ClickHouse HTTP | <http://clickhouse.k8s.tyrell.com.au> | `default` | `<REDACTED-SEE-VAULT>` |

## TCP Services (NodePort)

| Service | Host | Port | Username | Password |
|---------|------|------|----------|----------|
| PostgreSQL | k8s.tyrell.com.au | 30432 | `postgres` | `<REDACTED-SEE-VAULT>` |
| ClickHouse Native | k8s.tyrell.com.au | 30900 | `default` | `<REDACTED-SEE-VAULT>` |
| Kafka Bootstrap | k8s.tyrell.com.au | 9092 | - | - |

## Connection Examples

### PostgreSQL

```bash
# psql
psql -h k8s.tyrell.com.au -p 30432 -U postgres -d postgres
# password: <REDACTED-SEE-VAULT>

# Connection string ($PGPASSWORD from vault)
postgresql://postgres:$PGPASSWORD@k8s.tyrell.com.au:30432/postgres
```

### ClickHouse

```bash
# HTTP API ($CH_PASSWORD from vault)
curl "http://clickhouse.k8s.tyrell.com.au/?query=SELECT%201" \
  --user "default:$CH_PASSWORD"

# Native client
clickhouse-client -h k8s.tyrell.com.au --port 30900 \
  -u default --password "$CH_PASSWORD"
```

### Kafka (AutoMQ)

```bash
# kafkacat / kcat
kcat -b k8s.tyrell.com.au:9092 -L

# kafka-console-producer
kafka-console-producer.sh --bootstrap-server k8s.tyrell.com.au:9092 --topic test

# kafka-console-consumer
kafka-console-consumer.sh --bootstrap-server k8s.tyrell.com.au:9092 --topic test --from-beginning
```

### MinIO S3

```bash
# AWS CLI
aws --endpoint-url http://s3.k8s.tyrell.com.au s3 ls \
  --access-key admin --secret-key <REDACTED-SEE-VAULT>

# mc client
mc alias set tyrell http://s3.k8s.tyrell.com.au admin <REDACTED-SEE-VAULT>
mc ls tyrell
```

## Internal K8s DNS (cluster only)

For applications running inside the cluster:

| Service | Internal Endpoint |
|---------|------------------|
| AutoMQ | `automq-0.automq-headless.automq.svc.cluster.local:9092` |
| PostgreSQL | `tyrell-pg-rw.postgresql.svc.cluster.local:5432` |
| MinIO | `minio.minio.svc.cluster.local:9000` |
| Prometheus | `prometheus.monitoring.svc.cluster.local:9090` |
| Grafana | `grafana.monitoring.svc.cluster.local:3000` |
| ClickHouse | `clickhouse-clickhouse.clickhouse.svc.cluster.local:8123` |

## SSH Access

```bash
ssh luser@10.1.2.240
# or
ssh luser@k8s.tyrell.com.au
```

## Notes

- All HTTP services route through Envoy Gateway on port 80
- TCP services (PostgreSQL, ClickHouse native, Kafka) use NodePorts directly
- DNS wildcard `*.k8s.tyrell.com.au` resolves to `10.1.2.240`
- Credentials are for POC only - do not use in production
