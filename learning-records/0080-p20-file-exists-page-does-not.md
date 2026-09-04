# P2.0 concept held — the file exists; the page does not

They counted five `kind`s on a real Trace, confirmed `/__supervisualizer__/` is a 404, and did not wire the URL. The file they pasted is `GET /` (`index`, `restaurantAPI.views.index`), not the canonical menuitem page — same five HTML-view kinds (`receive_input`, `route`, `attach_context`, `render_output`, `send_response`), `capture_errors: []`. Do not make them redo the menuitem hit for this. Next is P2.1 (`include` the package’s URLs). The “send” mix-up from LR-0067 did not recur: they treated the JSON as already written.
