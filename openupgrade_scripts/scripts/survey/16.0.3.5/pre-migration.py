from openupgradelib import openupgrade

_xmlids_renames = [
    ("survey.survey_form", "survey.survey_survey_view_form"),
    ("survey.survey_kanban", "survey.survey_survey_view_kanban"),
    ("survey.survey_tree", "survey.survey_survey_view_tree"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlids_renames)
