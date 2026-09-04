Altitude: mechanical

# product looks up menuitem, not cartitem

They completed the 0011 sentence: `product` searches the menuitem queryset and the match is a menuitem instance in `validated_data`. Floor for SlugRelatedField: the direction is string → queryset → instance, not instance → model.
