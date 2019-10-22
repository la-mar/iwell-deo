# import os
from sqlalchemy.sql import func

from iwell import db
from api.model_mixins import DataFrameMixin

# from flask import current_app

# app_settings = os.getenv("APP_SETTINGS")


# my_module = importlib.import_module("module.submodule")
# MyClass = getattr(my_module, "MyClass")
# instance = MyClass()
schema = "public"


class IntegrationLog(DataFrameMixin, db.Model):

    __tablename__ = "integration_log"
    # __table_args__ = {"schema": schema}

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    integrated_at = db.Column(db.DateTime(timezone=True), nullable=False)
    model_name = db.Column(db.String(), nullable=False)
    inserts = db.Column(db.Integer(), nullable=False, default=0)
    updates = db.Column(db.Integer(), nullable=False, default=0)
    deletes = db.Column(db.Integer(), nullable=False, default=0)
    updated_by = db.Column(db.String(), default=func.current_user(), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )


class User(DataFrameMixin, db.Model):

    __tablename__ = "users"
    # __table_args__ = {"schema": schema}

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=True)
    phone = db.Column(db.String(), nullable=True)
    user_type = db.Column(db.String(), nullable=True)  # type
    status = db.Column(db.String(), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )


class Well(DataFrameMixin, db.Model):

    __tablename__ = "wells"
    # __table_args__ = {"schema": schema}

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    well_name = db.Column(db.String(), nullable=True)
    well_type = db.Column(db.String(), nullable=True)
    well_alias = db.Column(db.String(), nullable=True)
    is_active = db.Column(db.Boolean(), default=False, nullable=False)
    latest_production_time = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    iwell_created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    iwell_updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    groups = db.relationship("WellGroupWell", backref="well", lazy=True)
    meters = db.relationship("Meter", backref="well", lazy=True)
    # meter_readings = db.relationship("MeterReading", backref="well", lazy=True)

    notes = db.relationship("WellNote", backref="well", lazy=True)
    fields = db.relationship("WellField", backref="well", lazy=True)
    # field_values = db.relationship("FieldValue", backref="well", lazy=True)
    production = db.relationship("Production", backref="well", lazy=True)


class Tank(DataFrameMixin, db.Model):

    __tablename__ = "tanks"
    # __table_args__ = {"schema": schema}

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    tank_name = db.Column(db.String(), nullable=True)
    tank_type = db.Column(db.String(), nullable=True)
    capacity = db.Column(db.Integer, nullable=True)
    multiplier = db.Column(db.Float, nullable=True)
    iwell_created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    iwell_updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    readings = db.relationship("TankReading", backref="tank", lazy=True)


class Meter(DataFrameMixin, db.Model):

    __tablename__ = "meters"
    # __table_args__ = {"schema": schema}

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    well_id = db.Column(
        db.Integer, db.ForeignKey(f"wells.id"), primary_key=True, nullable=False
    )
    meter_name = db.Column(db.String(), nullable=True)
    meter_order = db.Column(db.Integer, nullable=True)
    product_type = db.Column(db.String(), nullable=True)
    iwell_created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    iwell_updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    readings = db.relationship("MeterReading", backref="meter", lazy=True)


class Field(DataFrameMixin, db.Model):

    __tablename__ = "fields"
    # __table_args__ = {"schema": schema}

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    field_name = db.Column(db.String(), nullable=True)
    field_type = db.Column(db.String(), nullable=True)
    field_unit = db.Column(db.String(), nullable=True)
    field_order = db.Column(db.Integer, nullable=True)
    is_historic = db.Column(db.Boolean(), default=False, nullable=False)
    is_remembered = db.Column(db.Boolean(), default=False, nullable=False)
    is_required = db.Column(db.Boolean(), default=False, nullable=False)
    iwell_created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    iwell_updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    well_fields = db.relationship("WellField", backref="field", lazy=True)


class WellGroup(DataFrameMixin, db.Model):

    __tablename__ = "well_groups"
    # __table_args__ = {"schema": schema}

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    group_name = db.Column(db.String(), nullable=True)
    is_active = db.Column(db.Boolean(), default=False, nullable=False)
    group_latest_production_time = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    iwell_created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    iwell_updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    wells = db.relationship("WellGroupWell", backref="well_group", lazy=True)


class WellGroupWell(DataFrameMixin, db.Model):

    __tablename__ = "well_group_wells"
    # __table_args__ = {"schema": schema}

    group_id = db.Column(
        db.Integer, db.ForeignKey(f"well_groups.id"), primary_key=True, nullable=False
    )
    well_id = db.Column(
        db.Integer, db.ForeignKey(f"wells.id"), primary_key=True, nullable=False
    )
    iwell_created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    iwell_updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )


class WellTank(DataFrameMixin, db.Model):

    __tablename__ = "well_tanks"
    # __table_args__ = {"schema": schema}

    tank_id = db.Column(
        db.Integer, db.ForeignKey(f"tanks.id"), primary_key=True, nullable=False
    )
    well_id = db.Column(
        db.Integer, db.ForeignKey(f"wells.id"), primary_key=True, nullable=False
    )
    iwell_created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    iwell_updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )


class TankReading(DataFrameMixin, db.Model):

    __tablename__ = "tank_readings"
    # __table_args__ = {"schema": schema}

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    tank_id = db.Column(
        db.Integer, db.ForeignKey(f"tanks.id"), primary_key=True, nullable=False
    )
    reading_at = db.Column(db.DateTime(timezone=True), nullable=False)  # reading_time
    cut_feet = db.Column(db.Float, nullable=True, default=0)
    cut_inches = db.Column(db.Float, nullable=True, default=0)
    top_feet = db.Column(db.Float, nullable=True, default=0)
    top_inches = db.Column(db.Float, nullable=True, default=0)
    previous_cut_feet = db.Column(db.Float, nullable=True, default=0)
    previous_cut_inches = db.Column(db.Float, nullable=True, default=0)
    previous_top_feet = db.Column(db.Float, nullable=True, default=0)
    previous_top_inches = db.Column(db.Float, nullable=True, default=0)
    # updated_by = db.Column(
    #     db.Integer, db.ForeignKey(f"users.id"), nullable=False
    # )
    updated_by = db.Column(db.Integer, nullable=True)
    iwell_created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    iwell_updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    run_tickets = db.relationship("RunTicket", backref="tank_reading", lazy=True)


class WellNote(DataFrameMixin, db.Model):

    __tablename__ = "well_notes"
    # __table_args__ = {"schema": schema}

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    well_id = db.Column(
        db.Integer, db.ForeignKey(f"wells.id"), primary_key=True, nullable=False
    )
    noted_at = db.Column(db.DateTime(timezone=True), nullable=False)  # note_time
    message = db.Column(db.String(), nullable=True)
    author = db.Column(db.Integer, db.ForeignKey(f"users.id"), nullable=True)
    is_pumper_content = db.Column(db.Boolean)
    iwell_created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    iwell_updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )


class WellField(DataFrameMixin, db.Model):

    __tablename__ = "well_fields"
    # __table_args__ = {"schema": schema}

    field_id = db.Column(
        db.Integer, db.ForeignKey(f"fields.id"), primary_key=True, nullable=False
    )
    well_id = db.Column(
        db.Integer, db.ForeignKey(f"wells.id"), primary_key=True, nullable=False
    )
    # field_name = db.Column(db.String(), nullable=True)
    # field_type = db.Column(db.String(), nullable=True)
    # field_unit = db.Column(db.String(), nullable=True)
    # field_order = db.Column(db.Integer, nullable=True)
    # is_historic = db.Column(db.Boolean(), default=False, nullable=False)
    # is_remembered = db.Column(db.Boolean(), default=False, nullable=False)
    # is_required = db.Column(db.Boolean(), default=False, nullable=False)
    iwell_created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    iwell_updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    field_values = db.relationship("FieldValue", backref="well_field", lazy=True)


class FieldValue(DataFrameMixin, db.Model):

    __tablename__ = "field_values"
    __table_args__ = (
        db.ForeignKeyConstraint(
            ["field_id", "well_id"], [f"well_fields.field_id", f"well_fields.well_id"]
        ),
        # {"schema": schema},
    )
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    field_id = db.Column(db.Integer, nullable=False)
    well_id = db.Column(db.Integer, nullable=False)
    reading_at = db.Column(db.DateTime(timezone=True), nullable=False)
    value = db.Column(db.Float, nullable=False)
    updated_by = db.Column(db.Integer, nullable=True)
    iwell_created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    iwell_updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )


class MeterReading(DataFrameMixin, db.Model):

    __tablename__ = "meter_readings"
    __table_args__ = (
        db.ForeignKeyConstraint(
            ["meter_id", "well_id"], [f"meters.id", f"meters.well_id"]
        ),
        # {"schema": schema},
    )

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    meter_id = db.Column(db.Integer, nullable=False)
    well_id = db.Column(db.Integer, nullable=False)
    reading_at = db.Column(db.DateTime(timezone=True), nullable=False)
    value = db.Column(db.Float, nullable=False)
    previous_value = db.Column(db.Float, nullable=False)
    updated_by = db.Column(db.Integer, nullable=True)
    iwell_created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    iwell_updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )


class Production(DataFrameMixin, db.Model):

    __tablename__ = "production"
    # __table_args__ = {"schema": schema}

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    well_id = db.Column(db.Integer, db.ForeignKey(f"wells.id"), nullable=False)
    produced_at = db.Column(db.DateTime(timezone=True), nullable=False)
    oil = db.Column(db.Float, nullable=False, default=0)
    gas = db.Column(db.Float, nullable=False, default=0)
    water = db.Column(db.Float, nullable=False, default=0)
    is_operating = db.Column(db.Boolean, nullable=True, default=False)
    hours_on = db.Column(db.Integer, nullable=False)
    normal_hours_on = db.Column(db.Integer, nullable=False)
    reported_date = db.Column(db.Date(), nullable=False)
    updated_by = db.Column(db.Integer, nullable=True)
    iwell_created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    iwell_updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    # prod_date as CONVERT([date],[prod_datetime]),
    # prod_year as datepart(year,[prod_datetime]),
    # prod_month as datepart(month,[prod_datetime]),
    # prod_day as datepart(day,[prod_datetime]),


class RunTicket(DataFrameMixin, db.Model):

    __tablename__ = "run_tickets"
    __table_args__ = (
        db.ForeignKeyConstraint(
            ["tank_id", "reading_id"], [f"tank_readings.tank_id", f"tank_readings.id"]
        ),
        # {"schema": schema},
    )

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    tank_id = db.Column(db.Integer, nullable=False)
    reading_id = db.Column(db.Integer, nullable=False)
    ticket_date = db.Column(db.Date(), nullable=False)
    run_ticket_number = db.Column(db.String(), nullable=False, default="")
    total = db.Column(db.Float, nullable=True)
    product_type = db.Column(db.String(), nullable=False, default="")
    picture_url = db.Column(db.String(), nullable=False, default="")
    comments = db.Column(db.String(), nullable=False, default="")
    updated_by = db.Column(db.Integer, nullable=True)
    iwell_created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    iwell_updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )

