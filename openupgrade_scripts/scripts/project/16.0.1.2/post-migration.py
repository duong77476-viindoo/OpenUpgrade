from openupgradelib import openupgrade


def active_group_project_milestone(env):
    env["res.config.settings"].create({"group_project_milestone": True}).execute()


def _fill_default_project_task_user_rel_stage_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_task_user_rel rel
            SET stage_id = typ.id
        FROM project_task_type typ
        WHERE rel.stage_id IS NULL AND typ.user_id = rel.user_id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    active_group_project_milestone(env)
    openupgrade.load_data(env.cr, "project", "16.0.1.2/noupdate_changes.xml")
    _fill_default_project_task_user_rel_stage_id(env)
