# Middleware still a vague list; order unexplained

After lesson 0005 they dump `request.user` and session keys after `get_response`, but stated they only have a vague idea of what middleware does and do not know why the `MIDDLEWARE` list is ordered (or why inward vs outward). Do not treat P1.3 as conceptually closed. Next lesson is wrapping: `get_response` is the next waiter, first-in-list is the door, Auth after Session because Auth reads `request.session`.
