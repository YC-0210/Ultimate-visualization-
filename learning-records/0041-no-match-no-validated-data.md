# No match means no validated_data

They said `validated_data` is not filled when the slug is missing from the queryset. `is_valid` must return True before that dict is legal to read. Floor for the P1.7 probe: copy only on a True result.
