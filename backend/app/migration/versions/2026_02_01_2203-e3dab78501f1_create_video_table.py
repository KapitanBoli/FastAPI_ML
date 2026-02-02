"""Create video table

Revision ID: e3dab78501f1
Revises: 1bb50ad7cb3a
Create Date: 2026-02-01 22:03:26.373207

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "e3dab78501f1"
down_revision: Union[str, Sequence[str], None] = "1bb50ad7cb3a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "Video",
        sa.Column("id", sa.UUID(), server_default=sa.text("uuidv7()"), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_Video")),
    )
    op.create_index(op.f("ix_Video_id"), "Video", ["id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_Video_id"), table_name="Video")
    op.drop_table("Video")
