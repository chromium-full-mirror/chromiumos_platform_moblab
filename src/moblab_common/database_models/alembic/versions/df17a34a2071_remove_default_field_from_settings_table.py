"""remove default field from settings table;

Revision ID: df17a34a2071
Revises: 4b5c0da080d5
Create Date: 2021-01-08 16:21:53.016995

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "df17a34a2071"
down_revision = "4b5c0da080d5"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("moblab_settings", "default_value")


def downgrade():
    op.add_column(
        "moblab_settings",
        sa.Column("default_value", sa.String(length=65535), nullable=False),
    )
