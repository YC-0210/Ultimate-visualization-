Altitude: structural

# Model maps to the table; queryset is the collection

They now split `class menuitem` (model → table) from `menuitem.objects.all()` (queryset → collection of objects from the database). Remaining precision: the collection is not itself “a row”; a match is an instance.
