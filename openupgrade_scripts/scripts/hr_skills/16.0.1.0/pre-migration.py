from openupgradelib import openupgrade


def fill_skill_type_id_data(env):
    env.cr.execute(
        """
        SELECT f.translate
        FROM ir_model_fields f
        WHERE f.name = 'name' AND f.model = 'hr.skill.type'
        LIMIT 1
        """
    )
    res = env.cr.fetchall()
    if res and res[0][0]:
        openupgrade.logged_query(
            env.cr,
            """
            INSERT INTO hr_skill_type
            (name) SELECT jsonb_object_agg('en_US', 'Dummy Skill Type')
            RETURNING id;
            """,
        )
    else:
        openupgrade.logged_query(
            env.cr,
            """
            INSERT INTO hr_skill_type
            (name) VALUES ('Dummy Skill Type')
            RETURNING id;
            """,
        )

    skill_type_id = env.cr.fetchall()[0][0]

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_skill
        SET skill_type_id = %s
        WHERE skill_type_id IS NULL
        """,
        (skill_type_id,),
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_skill_type_id_data(env)
    # Create fake table for not triggering the compute method
    env.cr.execute(
        """CREATE TABLE hr_employee_hr_skill_rel
        (hr_employee_id integer, hr_skill_id integer)"""
    )
