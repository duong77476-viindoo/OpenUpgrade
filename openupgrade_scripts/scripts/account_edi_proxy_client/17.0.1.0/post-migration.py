# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _account_edi_proxy_client_user_fill_edi_mode(env):
    demo_state = env["ir.config_parameter"].get_param(
        "account_edi_proxy_client.demo", False
    )
    if demo_state:
        client_users = (
            env["account_edi_proxy_client.user"]
            .with_context(active_test=False)
            .search([])
        )
        client_users.write(
            {
                "edi_mode": "prod"
                if demo_state in ["prod", False]
                else "test"
                if demo_state == "test"
                else "demo"
            }
        )


@openupgrade.migrate()
def migrate(env, version):
    _account_edi_proxy_client_user_fill_edi_mode(env)
