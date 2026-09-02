# We never adopted OTLP; we borrowed two ids

Summarising LR-0073 they said "we aren't leaving the span format from OTLP" — backwards. Corrected: the Trace was never in OTLP; the borrowing is `trace_id` and `parent_id` (D5) and nothing else. Our stages carry `id` / `kind` / `label` / `data` / `source`, none of which OTel defines, and the schema contains no span. They had the second half right (no Collector; the panel reads the Trace directly). Also corrected the acronym: OTLP is the OpenTelemetry Protocol, while OLTP is online transaction processing — watch for that swap recurring.
