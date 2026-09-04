Altitude: structural

# There is no OTel receiver here; the panel is the reader

Reading lesson 0018's code they noticed the Trace does not match OTel's sample span JSON and asked whether that forces a custom receiver or an adapted OTel one. Established: neither. OTel's own note says those JSON examples "do not represent a specific format, and especially not OTLP/JSON"; "receiver" is a Collector component, and the architecture has no Collector, no OTLP and no backend. The panel is what reads the Trace, hand-written once in Phase 2 — that is D7's M+N bet. If D6's OTel lands for the tree, the in-process piece is a custom `SpanProcessor` (`OnStart` / `OnEnd` hooks), not a receiver. Also named the cost out loud: no OTLP means no free Jaeger/Grafana, but those render duration, not `menuitem instance`. Separately sharpened "time series" (a metrics term) to time-ordered filename.
