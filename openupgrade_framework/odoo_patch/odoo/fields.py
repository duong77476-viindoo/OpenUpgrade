import itertools

from openupgradelib import openupgrade

from odoo.fields import _String
from odoo.tools.sql import table_exists
from odoo.tools.translate import _get_translation_upgrade_queries


def _convert_db_column(self, model, column):
    _String._convert_db_column._original_method(self, model, column)
    # update all translatable fields
    # specialized implementation for converting from/to translated fields
    if (self.translate or column["udt_name"] == "jsonb") and table_exists(
        model._cr, "_ir_translation"
    ):
        for query in itertools.chain.from_iterable(
            _get_translation_upgrade_queries(model._cr, self)
        ):
            # We want to take the translation value instead
            query = query.replace(
                'ELSE t.value || m."%s" END' % self.name,
                'ELSE m."%s" || t.value END' % self.name,
            )
            openupgrade.logged_query(model._cr, query)


_convert_db_column._original_method = _String._convert_db_column
_String._convert_db_column = _convert_db_column
