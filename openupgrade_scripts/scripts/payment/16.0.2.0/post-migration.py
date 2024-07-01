from openupgradelib import openupgrade


def fill_payment_provider_is_published(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE payment_provider
            SET is_published = True
        WHERE state IN ('enabled', 'test')
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "payment", "16.0.2.0/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "payment.payment_acquirer_alipay",
            "payment.payment_acquirer_ogone",
            "payment.payment_acquirer_payulatam",
            "payment.payment_acquirer_payumoney",
            "payment.payment_acquirer_test",
        ],
    )
    fill_payment_provider_is_published(env)
