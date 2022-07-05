from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "crm_iap_enrich", "15.0.1.1/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "crm_iap_enrich",
        [
            "mail_message_lead_enrich_no_credit",
            "mail_message_lead_enrich_no_email",
            "mail_message_lead_enrich_notfound",
        ],
    )
