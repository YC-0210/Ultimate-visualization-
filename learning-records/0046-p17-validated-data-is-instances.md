Altitude: structural

# P1.7 validated_data holds instances

They posted `POST /api/cart/item/` (`廣式沙茶鍋`, `豬肉`, `九層花枝`). Body still had slug strings. `validations[0].data` had `menuitem instance` pk=2, `meattype instance` pk=1, `hotpotingredients instance` pk=1. SQL was the three slug lookups, then INSERT. Empty list on the HTML GET was the other view, not a probe bug.
