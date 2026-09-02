# P1.2 four fields print on a live CBV request

`GET /api/menuitem/經典原味鍋/` dumped `route` `api/menuitem/<str:slug>/`, `url_name` `menuitem_detail`, `view` `restaurantAPI.views.menuitemDetail`, `kwargs` `{"slug": "經典原味鍋"}`, HTTP 200. That is the class-based peel. A second dump on `GET /admin/` used the no-`view_class` branch (`django.contrib.admin.sites.AdminSite.index`, empty kwargs). Lesson 0002 also asked for `/login/`; not required to keep P1.2 ticked. Next is P1.3.
