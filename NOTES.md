# Teaching notes

## The two principles

1. **Capture is deterministic. The LLM explains; it never observes.** (`supervisualizer/ROADMAP.md`)
2. **If I can't see it all at once, I don't understand it yet.**

The second is why [`MAP.html`](MAP.html) exists. A part learned in isolation is a part that gets lost, so every lesson links back to the map and updates it, and no lesson is finished until it does. When a run of sessions has produced only small, local understandings, that is the signal to stop and teach the whole — see the `Altitude:` field on the learning records.

## Preferences

- **Logic over syntax.** Why the system behaves this way. Punctuation and style only when they change the observed behaviour.
- **Widgets that compute, not widgets that reveal.** A widget whose every state is a string written into the asset is a slideshow with buttons — it repeats the lesson in a second font. Prefer components that scrub, compute, or respond to a changed value. `assets/timeline.js` is the reusable one: a broad-granularity scrubber (stages, phases, events — never line-by-line) with three tenses, where **future shows no data** because nothing has observed it yet.
- **Copyable shape in the lesson, not in their file.** If they must type something and the shape is not obvious, put **two** code blocks: (1) a clean copyable snippet, (2) the same snippet with a comment on each line in concrete language (what that line does). Do not paste either into `middleware.py` until they have done the practice.
- **What lives where.** NOTES: preferences, lesson style, workspace facts, target-app examples. `learning-records/`: understandings and corrections, each tagged `Altitude: structural | mechanical`. [`MAP.html`](MAP.html): the whole topic at once — a mirror of the roadmap, never a second record of progress. Progress: [`supervisualizer/ROADMAP.md`](supervisualizer/ROADMAP.md) Status block — never “P1.x is done” here.
- **Teaching replies: as concise as possible.** No recap. Answer, then stop (or one short check).
- **When they say they have the concept, move on** (LR-0072). Drop the restatement drill and check the *code output* instead. Do not ask them to read a long print line back to you — pull the facts out of it yourself and hand back only what changes the code.

## Lesson HTML style

Follow this every time a lesson is generated.

- **Problem first.** One sentence they could repeat, before any Django API name. Example: “You already know the URL the browser sent. You do not yet know which of your routes Django picked.” Then two concrete facts on one real restaurant-app request, as have/need cards (`.facts` / `.fact.have` / `.fact.need`).
- **No analogies; simulate instead** (LR-0047, sharpened). The ban stands: no restaurant-floor stories (waiter, diner, ticket, menu, cook, plate, recipe, door, kitchen) in lessons, reference cards, captions, widgets, or teaching replies. Introduce a new word by quoting the official docs and pointing at one fact on a real restaurant-app request, then use that word. If the docs themselves use a metaphor (e.g. “onion”), quote it as their word and link the page — do not extend it.

  **What the ban does not license is more prose.** Dropping the analogy left a gap, and the default fill has been another paragraph — the wrong direction for a heavy visual learner. The replacement for an analogy is a **thing that can be driven**: a scrubber, a widget that computes, a real value at a real hop. Papert's point (via Victor) is that the Logo turtle works through *identification with a concrete object you can put yourself inside*, not through resemblance to something else. Ban the resemblance; keep the concrete object. When the honest options are a paragraph or a widget, build the widget.
- **Say which tier a word comes from** (LR-0068). Three tiers: framework words with official docs (`validated_data`, `execute_wrapper`), borrowed spec words (OTel span, LSP `SymbolKind`), and words coined in this repo (`Stage`, `Packet`, `Trace`, `Probe`, `Panel`, `Adapter`, `Kind`/`Label`). For tier 3 there are no official docs to quote — quote [`CONTEXT.md`](CONTEXT.md) and say it is this repo's word, so they do not go searching Django's docs for it.
- **Technical names only.** In running text, captions, widgets, quizzes, and later lessons. Current set: `route`, `view class`, `request`, `request.body`, `cookie`, `get_response`, `session`, `request.user`, `permission_classes`, `serializer_class`, `queryset`, `sql`, `is_valid`, `validated_data`, `model`, `instance`, `serializer`, `self`, `*args`, `**kwargs`, `template`, `context`, `render`, `function object`, `method object`, `kind`, `label`, `Trace`.
- **Visual of the mechanism** (have/need cards, type-hop) before a timing rule or a code edit.
- **Type in a gloss, not the sentence.** Running text stays vague (“the result”). Click-to-open `.gloss` (`assets/gloss.js`) names the type, quotes or closely paraphrases the official docs, and links the class page. Do not invent a type.

## Workspace

- Teaching files live at this folder’s root, not inside `supervisualizer/` (the installable package).
- Target app: `hotpot-restaurant-ordering-system` (`-/restaurant/`). Middleware is already first in `MIDDLEWARE`.
- They build by hand. `prototype/extract_all.py` is ideas-only; `match.func.cls` is a DRF extra, not Django’s documented `view_class`.

## Target app examples (always verify)

Target: `/Users/chen/Desktop/hotpot-restaurant-ordering-system/-/`

**Never invent a path.** Before a lesson names a URL, view, `url_name`, or slug: read `restaurant/urls.py` and `restaurantAPI/urls.py`, then query `db.sqlite3`. Do not copy slugs from `prototype/` (`classic-original`, `kimchi-hotpot`, `spicy-mala`, …).

Live rows as of 2026-08-28:

- menuitem: `經典原味鍋`, `廣式沙茶鍋`
- meattype: `豬肉`, `牛肉`, `羊五花`
- hotpotingredients: `九層花枝`, `香菇貢丸`

Two different “menuitem” URLs — do not mix them:

| | Path | View | `url_name` |
|---|---|---|---|
| JSON API | `/api/menuitem/<slug>/` | CBV `menuitemDetail` | `menuitem_detail` |
| HTML page | `/menuitem/<slug>/` | FBV `menuitem_detail` | `menuitem_page` |

Canonical practice URL: `GET /menuitem/經典原味鍋/` (HTML page, FBV `menuitem_detail`, `url_name` `menuitem_page`). They hit this path for capture. The JSON API is a different view — use it only when the task needs a class view or serializer (`permission_classes`, `serializer_class`, P1.7). Do not mix the two paths’ names.

The customize form `POST`s `/api/cart/item/` — Phase 1 “done when” (P1.7), not the slug-walk example.
