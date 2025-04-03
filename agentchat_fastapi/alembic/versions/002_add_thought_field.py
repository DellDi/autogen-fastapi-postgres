"""添加thought字段

Revision ID: 002
Revises: 001
Create Date: 2025-04-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 添加thought字段到chat_messages表
    op.add_column('chat_messages', sa.Column('thought', sa.Text(), nullable=True))


def downgrade() -> None:
    # 删除thought字段
    op.drop_column('chat_messages', 'thought')
