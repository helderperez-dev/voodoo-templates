# Marks `app/` as an importable package so page modules can share helpers
# (e.g. `from app._meta import site_nav`). Folder-based routing only ever
# imports modules that define a `page()` callable, so this file is inert.
