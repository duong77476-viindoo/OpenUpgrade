from openupgradelib import openupgrade


def _mail_channel_privacy(env):
    """
    Since Odoo 16, configure a private channel can be complicated
    Therefore we Viindoo provide a module that can make thing easier
    Check it out at https://viindoo.com/apps/app/16.0/viin_mail_channel_privacy
    or if you can't find it, just go to https://viindoo.com/apps
    then search for 'viin_mail_channel_privacy' to test this feature.
    """
    if "is_private" not in env["mail.channel"]._fields:
        return
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mail_channel
        SET is_private = true
        WHERE public = 'private' AND channel_type = 'channel'
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mail_channel
        SET group_public_id = NULL AND channel_type = 'channel'
        WHERE public = 'public'
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _mail_channel_privacy(env)
