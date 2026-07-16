# Endpoint metrics | Modal Docs

Source: https://modal.com/docs/guide/endpoint-metrics

---

---

Copy page

# Endpoint metrics

Every endpoint reports live inference metrics so you can see how itâs performing
under real traffic â latency, throughput, and how many requests are in flight.
Open an endpoint from the **Endpoints** tab and go to the **Activity** view to
see them.

There are two types of metrics available:

* **Inference metrics** â LLM engine-specific metrics designed to give you more
  performance observability.
* **Server metrics** â the standard Modal container health metrics.

## What the metrics meanÂ

**Latency** (reported as p50 / p95 / p99):

* **Time to first token (TTFT)** â how long after a request arrives before the
  first output token streams back. The number users feel first.
* **Inter-token latency (ITL)** â average gap between successive output tokens.
  Drives perceived âtyping speed.â
* **End-to-end latency (E2E)** â total time to complete a request.

**Throughput:**

* **Requests per second (QPS)** â request arrival rate.
* **Token throughput** â tokens/second, split into prefill (processing the
  prompt, with a separate line for cache-hit tokens) and decode (generating
  output).

**Request load:**

* **Request activity** â the rate of requests arriving at and completing on the
  endpoint over time.
* **Running** â requests currently being processed.
* **Queued** â requests waiting for a free slot. Sustained queueing means the
  fleet is saturated and scaling up.

**Speculative decoding** (only for recipes that use it) â the average number of
draft tokens accepted per step; higher means speculation is paying off.

## CaveatsÂ

* **Metrics need traffic.** Latency and throughput are computed over recent
  rolling windows; an idle or scaled-to-zero endpoint shows no current data.
* **Cold starts skew early numbers.** The first requests after a scale-up
  include model load time. Look at steady-state windows when evaluating
  performance.
* **Percentiles need volume.** p95/p99 are only meaningful once enough requests
  have accumulated in the window.
* Endpoint metrics are available in the dashboard. To get repeatable performance
  numbers under a controlled load, [run a
  benchmark](/docs/guide/endpoint-benchmarks).

[Endpoint metrics](#endpoint-metrics)[What the metrics mean](#what-the-metrics-mean)[Caveats](#caveats)