import re

from lxml import etree
from openupgradelib import openupgrade


def _rename_field_on_filters(cr, model, old_field, new_field):
    # Example of replaced domain: [['field', '=', self], ...]
    # TODO: Rename when the field is part of a submodel (ex. m2one.field)
    cr.execute(
        """
        UPDATE ir_filters
        SET domain = regexp_replace(domain, %(old_pattern)s, %(new_pattern)s , 'g')
        WHERE model_id = %%s
            AND domain ~ %(old_pattern)s
        """
        % {
            "old_pattern": r"""$$('|")%s('|")$$""" % old_field,
            "new_pattern": r"$$\1%s\2$$" % new_field,
        },
        (model,),
    )
    # Examples of replaced contexts:
    # {'group_by': ['field', 'other_field'], 'other_key':value}
    # {'group_by': ['date_field:month']}
    # {'other_key': value, 'group_by': ['other_field', 'field']}
    # {'group_by': ['other_field'],'col_group_by': ['field']}
    cr.execute(
        r"""
        UPDATE ir_filters
        SET context = regexp_replace(
            context, %(old_pattern)s, %(new_pattern)s, 'g'
        )
        WHERE model_id = %%s
            AND context ~ %(old_pattern)s
        """
        % {
            "old_pattern": (
                r"""$$('group_by'|'col_group_by'|'graph_groupbys'
                       |'pivot_measures'|'pivot_row_groupby'|'pivot_column_groupby'
                    ):([\s*][^\]]*)"""
                r"'%s(:day|:week|:month|:year){0,1}'(.*?\])$$"
            )
            % old_field,
            "new_pattern": r"$$\1:\2'%s\3'\4$$" % new_field,
        },
        (model,),
    )
    # Examples of replaced contexts:
    # {'graph_measure': 'field'
    cr.execute(
        r"""
        UPDATE ir_filters
        SET context = regexp_replace(
            context, %(old_pattern)s, %(new_pattern)s, 'g'
        )
        WHERE model_id = %%s
            AND context ~ %(old_pattern)s
        """
        % {
            "old_pattern": (
                r"$$'graph_measure':([\s*])'%s(:day|:week|:month|:year){0,1}'$$"
            )
            % old_field,
            "new_pattern": r"$$'graph_measure':\1'%s\2'$$" % new_field,
        },
        (model,),
    )


def _rename_field_on_dashboard(env, model, old_field, new_field):
    dashboard_view_data = env["ir.ui.view.custom"].search([])
    for r in dashboard_view_data:
        parsed_arch = etree.XML(r.arch)
        act_window_ids = parsed_arch.xpath("//action/@name")
        actions = env["ir.actions.act_window"].search(
            [
                ("id", "in", act_window_ids),
                ("res_model", "=", model),
            ]
        )
        for action in actions:
            condition_for_element = "//action[@name='{}']".format(action.id)
            condition_for_domain = "//action[@name='{}']/@domain".format(action.id)
            condition_for_context = "//action[@name='{}']/@context".format(action.id)
            arch_element = parsed_arch.xpath(condition_for_element)
            for index in range(len(arch_element)):
                arch_domain = arch_element[index].xpath(condition_for_domain)[index]
                arch_context = arch_element[index].xpath(condition_for_context)[index]

                arch_context = re.sub(
                    r"""('group_by'|'col_group_by'|'graph_groupbys'
                        |'pivot_measures'|'pivot_row_groupby'|'pivot_column_groupby'
                        ):([\s*][^\]]*)'%s(:day|:week|:month|:year){0,1}'(.*?\])"""
                    % old_field,
                    r"\1:\2'%s\3'\4" % new_field,
                    arch_context,
                )

                arch_context = re.sub(
                    r"""'graph_measure':([\s*])'%s(:day|:week|:month|:year){0,1}'"""
                    % old_field,
                    r"'graph_measure':\1'%s\2'" % new_field,
                    arch_context,
                )

                arch_domain = re.sub(
                    r"""('|")%s('|")""" % old_field,
                    r"\1%s\2" % new_field,
                    arch_domain,
                )

                arch_element[index].set("domain", arch_domain)
                arch_element[index].set("context", arch_context)

            new_arch = etree.tostring(parsed_arch, encoding="unicode")

            r.write({"arch": new_arch})


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.convert_field_to_html(
        env.cr, "hr_employee", "departure_description", "departure_description"
    )
    openupgrade.convert_field_to_html(env.cr, "hr_job", "description", "description")
    _rename_field_on_filters(env.cr, "hr.employee", "work_location", "work_location_id")
    _rename_field_on_filters(
        env.cr, "hr.employee.public", "work_location", "work_location_id"
    )
    _rename_field_on_dashboard(env, "hr.employee", "work_location", "work_location_id")
    _rename_field_on_dashboard(
        env, "hr.employee.public", "work_location", "work_location_id"
    )
