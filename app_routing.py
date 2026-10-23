# app_routing.py

class MattersRouter:
    """
    Routes the 'matters' app to the 'matters_db' database.
    Everything else (all of Mayan's apps) stays on 'default',
    which is Mayan's own database.
    """

    route_app_labels = {"matters"}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "matters_db"
        return "default"

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "matters_db"
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        # Django does not support cross-database FKs, so this
        # only affects same-database relations. Returning True
        # is safe here.
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == "matters_db"
        return db == "default"
