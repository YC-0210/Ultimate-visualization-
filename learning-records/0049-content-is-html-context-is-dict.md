# content is the HTML; context is the dict

They called the dict “content.” Floor: `response.content` is the HTML bytes (P1.6). The dict the view passed to `render` is `context`. Not every value in it is a model instance (`item` is; `meats` is a queryset; `slug` is a str).
