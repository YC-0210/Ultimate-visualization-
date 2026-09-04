Altitude: mechanical

# validated_data is the typed dict after is_valid

They already know `is_valid` deserializes into `validated_data`, a dict whose values can be live model instances (`menuitem(pk=…)`). Next gap is what actually performs that string→row hop (`SlugRelatedField`), not the dict itself.
