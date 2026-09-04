Altitude: mechanical

# P1.8 context holds the live objects the template reads

They hit `GET /menuitem/經典原味鍋/` (`menuitem_page`). `templates[0].template` is `includes/menuitem-detail.html`. `item` is `menuitem instance` pk=1; `meats` / `ingredients` are QuerySets; `slug` is str; `table_number` is None. `validations` is `[]` — HTML view, not a probe bug. `response.content` is already the HTML string.
