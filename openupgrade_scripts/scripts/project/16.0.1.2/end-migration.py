import logging
from itertools import groupby

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)

def _fill_stage_id_for_personal_user_stage(env):
    """
    After finish running migration for project module
    go to project -> my task and we may see a column whose name is 'None' and may contain some tasks
    but we can not click to see it (only in kanban view)
    The reason is the 'stage_id' field of 'project.task.stage.personal' is empty
    When it come to personal stage,
    odoo compute the field 'personal_stage_id' from 'project.task.stage.personal',
    but as i mention above 'stage_id' some how is empty
    so we face that noisy bug above
    This end-migration is to find if there is such a case like that
    then we will create a Stage call 'Undefined' then fill it in 'stage_id'
    """
    # TODO: we still need to find why the stage_id of project.task.stage.personal are being empty
    empty_stage_personal_user_stages = env["project.task.stage.personal"].search(
        [("stage_id", "=", False), ("user_id.active", "=", True)]
    )
    if empty_stage_personal_user_stages:
        _logger.debug("Here is the record ids that have stage_id empty on project.task.stage.personal model: ", empty_stage_personal_user_stages.ids)
        for user, grouped_personal_stage_lines in groupby(empty_stage_personal_user_stages, lambda stage: stage.user_id):
            to_fill = env["project.task.type"]
            # First we take priority if task_id.stage_id is not empty
            # then fill stage_id of "project.task.stage.personal" with it
            for line in grouped_personal_stage_lines:
                if line.task_id.stage_id:
                    line.stage_id = line.task_id.stage_id
                else:
                    to_fill |= line
            # then fill for those which have taks_id.stage_id is empty
            # this step where we will create a "project.task.type" record
            if to_fill:
                undefine_task_stage = env["project.task.type"].create(
                    {
                        'name': "Undefined",
                        'user_id': user.id,
                    }
                )
                to_fill.stage_id = undefine_task_stage

@openupgrade.migrate()
def migrate(env, version):
    _fill_stage_id_for_personal_user_stage(env)
