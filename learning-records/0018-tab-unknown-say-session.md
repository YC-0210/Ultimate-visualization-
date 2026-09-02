# “Tab” was unknown — say session, give table_number

They did not know what “tab” meant. Do not use it. The session is a dictionary Django stores on the server and looks up with the cookie’s `sessionid`. Concrete: `GET /?table_number=3` writes `request.session['table_number']`; later URLs omit `3`, but the dictionary still has it. The cookie is only the lookup number.
