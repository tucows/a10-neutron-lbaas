#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""add devices table

Revision ID: 9efdb20bd914
Revises: c4e1caaa618d
Create Date: 2019-02-08 15:28:56.644296

"""

# revision identifiers, used by Alembic.
revision = '9efdb20bd914'
down_revision = 'c4e1caaa618d'
branch_labels = None
depends_on = None

from alembic import op  # noqa
import sqlalchemy as sa  # noqa

def upgrade():
    op.create_table(
        'a10_devices',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('host', sa.String(255), nullable=False),
        sa.Column('username', sa.String(255), nullable=False),
        sa.Column('password', sa.String(255), nullable=False),
        sa.Column('api_version', sa.String(255), nullable=False),
        sa.Column('port', sa.Integer, nullable=False),
    )
    pass

def downgrade():
    op.drop_table('a10_devices')
    pass
