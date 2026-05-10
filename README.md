# RSigma Dynamic Pipelines: Live Threat Intel Demo

Companion repository for the article **"Wiring Live Threat Intel into Sigma Detection with Dynamic Pipelines"** on [mostafa.dev](https://mostafa.dev).

This repo demonstrates RSigma v0.10.0's dynamic pipeline feature by wiring two public threat intelligence sources into Sigma detection rules at runtime, without modifying the rules themselves.

## What is in this repo

```
pipelines/threat_intel.yml    # Dynamic pipeline with HTTP + command sources
rules/
  botnet_c2_connection.yml    # Sigma rule: firewall C2 IP detection
  lummac2_dns_query.yml       # Sigma rule: DNS C2 domain detection
scripts/extract_iocs.py       # ioc-finder wrapper for command source
advisories/aa25-141b.txt      # CISA AA25-141B LummaC2 advisory text
events/
  firewall.jsonl              # Sample firewall events (3 match, 3 benign)
  dns.jsonl                   # Sample DNS events (3 match, 3 benign)
```

## Data sources

| Source | Type | What it provides | Refresh |
|--------|------|-----------------|---------|
| [Feodo Tracker](https://feodotracker.abuse.ch/blocklist/) | HTTP | Botnet C2 IPs (Emotet, Dridex, TrickBot, QakBot) | Every 5 min |
| [CISA AA25-141B](https://www.cisa.gov/news-events/cybersecurity-advisories/aa25-141b) via [ioc-finder](https://github.com/fhightower/ioc-finder) | Command | LummaC2 C2 domains (~114 domains) | Once |

Both sources are free and require no authentication.

## Prerequisites

- [RSigma](https://github.com/timescale/rsigma) v0.10.0 or later
- Python 3.9+ with `ioc-finder` installed

```bash
pip install ioc-finder
```

## Quick start

### 1. Inspect the resolved sources

See what the pipeline fetches from Feodo Tracker and extracts from the CISA advisory:

```bash
rsigma resolve -p pipelines/threat_intel.yml --pretty
```

Inspect a single source:

```bash
rsigma resolve -p pipelines/threat_intel.yml -s c2_ips --pretty
rsigma resolve -p pipelines/threat_intel.yml -s advisory_domains --pretty
```

### 2. Run with the daemon

Dynamic source resolution requires `rsigma daemon`, which uses the `rsigma-runtime` crate
to fetch HTTP endpoints, execute commands, and manage refresh intervals. The `rsigma eval`
CLI command operates on static pipelines only, because `rsigma-eval` is a pure synchronous
evaluation library with no I/O dependencies.

Start the daemon with the dynamic pipeline and rules:

```bash
rsigma daemon \
  --rules rules/ \
  --pipeline pipelines/threat_intel.yml \
  --input http \
  --api-addr 127.0.0.1:8080
```

Then send events to the daemon:

```bash
curl -X POST http://127.0.0.1:8080/api/v1/events \
  -H "Content-Type: application/json" \
  -d @events/firewall.jsonl
```

## How it works

1. The pipeline YAML declares two `sources`: an HTTP source that fetches C2 IPs from Feodo Tracker, and a command source that runs `ioc-finder` against the CISA advisory text.

2. At startup, the daemon resolves both sources, extracting IP addresses and domains respectively.

3. The `vars` section maps resolved data to template variables (`${source.c2_ips}`, `${source.advisory_domains}`).

4. The `value_placeholders` transformation replaces `%c2_ips%` and `%advisory_domains%` in the Sigma rules with the resolved values.

5. The Sigma rules never change. Detection adapts as the feeds update.

## Related articles

1. [Pattern Detection and Correlation in JSON Logs](https://mostafa.dev) (Feb 2026)
2. [Streaming Logs to RSigma for Real-Time Detection](https://mostafa.dev) (Apr 2026)
3. [Building a Detection Layer on PostgreSQL with Sigma Rules](https://mostafa.dev) (Apr 2026)
4. [Security Observability with RSigma and the LGTM Stack](https://mostafa.dev) (May 2026)
5. **Wiring Live Threat Intel into Sigma Detection with Dynamic Pipelines** (this article)

## License

MIT
