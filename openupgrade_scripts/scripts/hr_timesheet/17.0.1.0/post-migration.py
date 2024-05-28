from openupgradelib import openupgrade


def _project_update_fill_timesheet(env):
    updates = env["project.update"].with_context(active_test=False).search([])
    for update in updates:
        project = update.project_id
        encode_uom = project.company_id.timesheet_encode_uom_id
        if not encode_uom:
            continue
        ratio = env.ref("uom.product_uom_hour").ratio / encode_uom.ratio
        update.write(
            {
                "uom_id": encode_uom,
                "allocated_time": round(project.allocated_hours / ratio),
                "timesheet_time": round(project.total_timesheet_time / ratio),
            }
        )


@openupgrade.migrate()
def migrate(env, version):
    _project_update_fill_timesheet(env)
