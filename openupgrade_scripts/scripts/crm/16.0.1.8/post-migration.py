from openupgradelib import openupgrade


def _rename_mailing_domain_for_lost_reason(env):
    """
    Since lost_reason -> lost_reason_id
    we need to replace that in mailing_domain field
    of mailing.mailing model
    """
    # TODO: move this to openupgradelib, see this discussion
    # https://github.com/OCA/OpenUpgrade/pull/3892
    if openupgrade.column_exists(env.cr, "mailing_mailing", "mailing_domain"):
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE mailing_mailing mm
            SET mailing_domain = regexp_replace(
                mailing_domain, %(old_pattern)s, %(new_pattern)s, 'g'
            )
            FROM ir_model im
            WHERE mm.mailing_model_id = im.id
                AND im.model = %%s
                AND mailing_domain ~ %(old_pattern)s
            """
            % {
                "old_pattern": r"""$$('|")%s('|")$$""" % "lost_reason",
                "new_pattern": r"$$\1%s\2$$" % "lost_reason_id",
            },
            ("crm.lead",),
        )


@openupgrade.migrate()
def migrate(env, version):
    _rename_mailing_domain_for_lost_reason(env)
