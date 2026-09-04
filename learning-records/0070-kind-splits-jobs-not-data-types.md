Altitude: structural

# kind splits jobs; `type` inside encode is the data type

Answering lesson 0017's check they got `trace_id` right (one request as a unit; extended with P4.3's browser-generated id). Two floors on `kind`: they called it "our own version of SpanKind" — it is a separate field with LSP's `SymbolKind` as prior art (D7), and the two would coexist on a stage span rather than replace each other. And they said it splits "different data type apart" — it splits lifecycle *jobs*; the data type is the `type` key their `encode` already writes (`menuitem instance`). Watch this conflation in P1.9: `kind` / `label` / `type` are three fields that all sound like "type".
