from openupgradelib import openupgrade

_xmlids_renames = [
    (
        "payment_paypal.payment_acquirer_form",
        "payment_paypal.payment_provider_form",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlids_renames)
