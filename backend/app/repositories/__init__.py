"""Data-access layer (reserved).

Simple queries currently live inline in services/routers via the SQLAlchemy
session. As data-access grows, extract repository classes here to keep services
persistence-agnostic (Clean Architecture / Dependency Inversion).
"""
