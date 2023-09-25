# Copyright Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from uuid import uuid4

from odoo.models import BaseModel

from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG

_logger = logging.getLogger(__name__)

NEED_UPDATED_VIEWS_KEYS = ["website.record_cover"]


def unlink(self):
    """Don't break on unlink of obsolete records
    when called from ir.model::_process_end()

    This only adapts the base unlink method. If overrides of this method
    on individual models give problems, add patches for those as well.
    """
    if not self.env.context.get(MODULE_UNINSTALL_FLAG):
        return BaseModel.unlink._original_method(self)
    savepoint = str(uuid4)
    try:
        self.env.cr.execute(  # pylint: disable=sql-injection
            'SAVEPOINT "%s"' % savepoint
        )
        return BaseModel.unlink._original_method(self)
    except Exception as e:
        self.env.cr.execute(  # pylint: disable=sql-injection
            'ROLLBACK TO SAVEPOINT "%s"' % savepoint
        )
        _logger.warning(
            "Could not delete obsolete record with ids %s of model %s: %s",
            self.ids,
            self._name,
            e,
        )
    return False


unlink._original_method = BaseModel.unlink
BaseModel.unlink = unlink


def _load_records(self, data_list, update=False):
    for vals in data_list:
        xml_id = vals.get("xml_id", False)
        original_record = self.env.ref(xml_id, raise_if_not_found=False)
        arch_db = (vals.get("values") or {}).get("arch", False)
        if (
            xml_id
            and arch_db
            and original_record
            and hasattr(original_record, "_name")
            and original_record._name == "ir.ui.view"
            and "website_id" in original_record._fields
        ):
            related_records = self.env["ir.ui.view"].search(
                [
                    ("id", "!=", original_record.id),
                    ("type", "=", "qweb"),
                    ("website_id", "!=", False),
                    ("key", "=", original_record.key),
                    "|",
                    ("key", "in", NEED_UPDATED_VIEWS_KEYS),
                    "&",
                    ("arch_db", "=", original_record.arch_db),
                    ("inherit_id", "!=", False),
                ]
            )
            for rec in related_records:
                if not rec.model_data_id and not rec.xml_id:
                    rec.arch_db = arch_db
    return BaseModel._load_records._original_method(self, data_list, update)


_load_records._original_method = BaseModel._load_records
BaseModel._load_records = _load_records
