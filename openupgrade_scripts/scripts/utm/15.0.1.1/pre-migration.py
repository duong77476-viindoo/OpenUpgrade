from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(
        env,
        [
            ("utm.campaign", "utm_campaign", "is_website", "is_auto_campaign"),
        ],
    )
