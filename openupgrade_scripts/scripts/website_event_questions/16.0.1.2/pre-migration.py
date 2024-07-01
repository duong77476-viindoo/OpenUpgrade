from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.add_fields(
        env,
        [
            (
                "is_mandatory_answer",
                "event.question",
                "event_question",
                "boolean",
                False,
                "website_event_questions",
                True,
            )
        ],
    )
