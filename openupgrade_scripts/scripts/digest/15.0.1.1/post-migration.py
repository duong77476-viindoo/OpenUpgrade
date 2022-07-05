from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "digest", "15.0.1.1/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "digest",
        [
            "digest_mail_main",
        ],
    )
