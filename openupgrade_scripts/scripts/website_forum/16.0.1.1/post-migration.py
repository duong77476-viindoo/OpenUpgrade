from openupgradelib import openupgrade
from openupgradelib.openupgrade_160 import convert_string_bootstrap_4to5


def _bs5_field_migration(env):
    forums = env["forum.forum"].with_context(active_test=False).search([])
    for forum in forums:
        new_faq = convert_string_bootstrap_4to5(forum.faq)
        if forum.faq != new_faq:
            forum.faq = new_faq


@openupgrade.migrate()
def migrate(env, version):
    _bs5_field_migration(env)
