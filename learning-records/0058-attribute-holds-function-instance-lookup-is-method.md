# Template.render is a class attribute holding a function object

They asked whether `Template.render` is a method object or a class attribute. Floor: those are not two types for one lookup. `Template.render` is the **attribute** (the name on the class); its **value** is a **function object**. A **method object** is `t.render` — lookup on an instance. Do not call `Template.render` a method object.
