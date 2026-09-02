# “Hangs” meant sets request.user

They did not know “hangs a user on this request.” It only meant AuthenticationMiddleware fills the `user` pocket: `request.user = …`. Same object, a new name you can read. Do not use “hangs.”
