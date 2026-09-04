Altitude: structural

# "Stage" is this repo's word, not Django's

They asked whether `Stage` is an officially defined term or one invented here. It is coined by this project and defined in `CONTEXT.md`; Django and DRF never use it, and the nearest industry term is OpenTelemetry's span (D5). Underlying gap: they did not know that this project's vocabulary comes in three tiers — framework words (`validated_data`, `resolver_match`), borrowed spec words (OTel span, LSP `SymbolKind`), and repo-coined words (`Stage`, `Packet`, `Trace`, `Probe`, `Panel`, `Adapter`). Tier tells them whether searching official docs will find it, so lessons should name the tier when introducing a word.
