import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _m2m_to_o2m_plan_activity_type_ids(env):
    """
    The field 'plan_activity_type_ids' has changed
    from m2m to o2m, so we need to check the rel table (m2m table)
    between them then fill value for 'plan_id' at hr.plan.activity.type
    and after that ORM will do the rest for us
    """
    env.cr.execute(
        """
        SELECT array_agg(hr_plan_id) AS hr_plan_ids, hr_plan_activity_type_id
        FROM hr_plan_hr_plan_activity_type_rel
        GROUP BY hr_plan_activity_type_id
        """
    )
    for hr_plan_ids, hr_plan_activity_type_id in env.cr.fetchall():
        hr_plan_activity_type = env["hr.plan.activity.type"].browse(
            hr_plan_activity_type_id
        )
        hr_plans = env["hr.plan"].browse(hr_plan_ids)
        hr_plan_activity_type.plan_id = hr_plans[:1]
        if len(hr_plan_ids) > 1:
            for hr_plan in hr_plans[1:]:
                hr_plan_activity_type_copy = hr_plan_activity_type.copy()
                hr_plan_activity_type_copy.plan_id = hr_plan


def fill_master_department_id(cr):
    """Fill master_department_id based on parent_path"""
    openupgrade.logged_query(
        cr,
        """
        UPDATE hr_department
        SET master_department_id = split_part(parent_path, '/', 1)::int
        WHERE parent_path is not NULL;
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "hr", "16.0.1.1/noupdate_changes.xml")
    _m2m_to_o2m_plan_activity_type_ids(env)
    fill_master_department_id(env.cr)
