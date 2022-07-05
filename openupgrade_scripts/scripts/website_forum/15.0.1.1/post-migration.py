from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "website_forum", "15.0.1.1/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "website_forum",
        [
            "forum_post_template_new_answer",
            "forum_post_template_new_question",
            "forum_post_template_validation",
        ],
    )
