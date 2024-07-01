from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = '8050684b813d'
down_revision = 'eb17e6d226d2'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('section', schema=None) as batch_op:
        batch_op.add_column(sa.Column('promotion_id', sa.Integer(), nullable=True))
        batch_op.create_index('ix_section_promotion_id', ['promotion_id'], unique=False)
        batch_op.create_foreign_key('fk_section_promotion_id', 'promotion', ['promotion_id'], ['id'])

def downgrade():
    with op.batch_alter_table('section', schema=None) as batch_op:
        batch_op.drop_constraint('fk_section_promotion_id', type_='foreignkey')
        batch_op.drop_index('ix_section_promotion_id')
        batch_op.drop_column('promotion_id')
