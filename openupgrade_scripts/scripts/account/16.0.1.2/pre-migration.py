from openupgradelib import openupgrade

ACCOUNT_TYPE = [
    ("account.data_account_type_receivable", "asset_receivable"),
    ("account.data_account_type_payable", "liability_payable"),
    ("account.data_account_type_liquidity", "asset_cash"),
    ("account.data_account_type_credit_card", "liability_credit_card"),
    ("account.data_account_type_current_assets", "asset_current"),
    ("account.data_account_type_non_current_assets", "asset_non_current"),
    ("account.data_account_type_prepayments", "asset_prepayments"),
    ("account.data_account_type_fixed_assets", "asset_fixed"),
    ("account.data_account_type_current_liabilities", "liability_current"),
    ("account.data_account_type_non_current_liabilities", "liability_non_current"),
    ("account.data_account_type_equity", "equity"),
    ("account.data_unaffected_earnings", "equity_unaffected"),
    ("account.data_account_type_revenue", "income"),
    ("account.data_account_type_other_income", "income_other"),
    ("account.data_account_type_expenses", "expense"),
    ("account.data_account_type_depreciation", "expense_depreciation"),
    ("account.data_account_type_direct_costs", "expense_direct_cost"),
    ("account.data_account_off_sheet", "off_balance"),
]


_xmlids_renames = [
    (
        "sale.group_delivery_invoice_address",
        "account.group_delivery_invoice_address",
    ),
]

_fields_renames = [
    (
        "account.analytic.line",
        "account_analytic_line",
        "move_id",
        "move_line_id",
    ),
    (
        "account.payment.term.line",
        "account_payment_term_line",
        "day_of_the_month",
        "days_after",
    ),
    (
        "account.tax.repartition.line.template",
        "account_tax_repartition_line_template",
        "minus_report_line_ids",
        "minus_report_expression_ids",
    ),
    (
        "account.tax.repartition.line.template",
        "account_tax_repartition_line_template",
        "plus_report_line_ids",
        "plus_report_expression_ids",
    ),
]
_models_renames = [
    ("account.tax.report", "account.report"),
    ("account.tax.carryover.line", "account.report.external.value"),
    ("account.tax.report.line", "account.report.line"),
]
_tables_renames = [
    ("account_tax_report", "account_report"),
    ("account_tax_carryover_line", "account_report_external_value"),
    ("account_tax_report_line", "account_report_line"),
]


def _fast_fill_account_account_type(env, model, table):
    if not openupgrade.column_exists(env.cr, table, "account_type"):
        openupgrade.add_fields(
            env,
            [
                (
                    "account_type",
                    model,
                    table,
                    "selection",
                    False,
                    "account",
                )
            ],
        )
    data_query = """SELECT res_id FROM ir_model_data
        WHERE module='%s' AND name='%s'"""
    for (account_type_old, account_type_new) in ACCOUNT_TYPE:
        get_data_query = data_query % tuple(account_type_old.split("."))
        query = f"""
            WITH account_type_old AS (
                SELECT id AS account_id
                FROM account_account
                WHERE user_type_id IN (
                    {get_data_query}
                )
            )
            UPDATE {table}
            SET account_type = '{account_type_new}'
            WHERE id IN (SELECT account_id FROM account_type_old)
        """
        openupgrade.logged_query(env.cr, query)


def _delete_sql_constraints(env):
    # Delete constraints to recreate it
    openupgrade.delete_sql_constraint_safely(
        env, "account", "account_journal", "code_company_uniq"
    )
    openupgrade.delete_sql_constraint_safely(
        env, "account", "account_move_line", "check_accountable_required_fields"
    )
    openupgrade.delete_sql_constraint_safely(
        env, "account", "account_move_line", "check_amount_currency_balance_sign"
    )
    openupgrade.delete_sql_constraint_safely(
        env, "account", "account_move_line", "check_credit_debit"
    )


def _account_analytic_line_fast_fill_journal_id(env):
    if not openupgrade.column_exists(env.cr, "account_analytic_line", "journal_id"):
        openupgrade.add_fields(
            env,
            [
                (
                    "journal_id",
                    "account.analytic.line",
                    "account_analytic_line",
                    "many2one",
                    False,
                    "account",
                )
            ],
        )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_analytic_line AS aal
        SET journal_id = (
            SELECT journal_id
                FROM account_move_line AS aml
                WHERE aml.id = aal.move_line_id
            LIMIT 1
        )
        """,
    )


def _account_bank_statement_line_fast_fill_internal_index(env):
    if not openupgrade.column_exists(
        env.cr, "account_bank_statement_line", "internal_index"
    ):
        openupgrade.add_fields(
            env,
            [
                (
                    "internal_index",
                    "account.bank.statement.line",
                    "account_bank_statement_line",
                    "char",
                    False,
                    "account",
                )
            ],
        )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_bank_statement_line stmt
        SET internal_index = concat(
            to_char(am.date, 'YYYYMMDD'),
            lpad((2147483647 - stmt.sequence)::text, 10, '0'),
            lpad(am.id::text, 10, '0')
        )
        FROM account_move am
        WHERE stmt.move_id = am.id;
        """,
    )


def _account_bank_statement_fast_fill_first_line_index(env):
    if not openupgrade.column_exists(
        env.cr, "account_bank_statement", "first_line_index"
    ):
        openupgrade.add_fields(
            env,
            [
                (
                    "first_line_index",
                    "account.bank.statement",
                    "account_bank_statement",
                    "char",
                    False,
                    "account",
                )
            ],
        )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_bank_statement AS stmt
        SET first_line_index = (
            SELECT internal_index
            FROM account_bank_statement_line
            WHERE statement_id = stmt.id
            ORDER BY statement_id
            LIMIT 1
        );
        """,
    )


def _account_bank_statement_fast_fill_is_complete(env):
    if not openupgrade.column_exists(env.cr, "account_bank_statement", "is_complete"):
        openupgrade.add_fields(
            env,
            [
                (
                    "is_complete",
                    "account.bank.statement",
                    "account_bank_statement",
                    "boolean",
                    False,
                    "account",
                ),
            ],
        )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_bank_statement AS stmt
        SET is_complete = (
            CASE
                WHEN EXISTS (
                    SELECT 1
                    FROM account_bank_statement_line
                    WHERE statement_id = stmt.id
                    AND stmt.state = 'posted'
                    AND stmt.balance_end = stmt.balance_end_real
                    LIMIT 1
                ) THEN true
            ELSE false
        END
        );
        """,
    )


def _account_payment_fast_fill_amount_company_currency_signed(env):
    if not openupgrade.column_exists(
        env.cr, "account_payment", "amount_company_currency_signed"
    ):
        openupgrade.add_fields(
            env,
            [
                (
                    "amount_company_currency_signed",
                    "account.payment",
                    "account_payment",
                    "monetary",
                    False,
                    "account",
                )
            ],
        )
    # TODO: consider fill value


def _account_move_fast_fill_display_type(env):
    """
    Respectively Fill display type is Null AND
    Case 1: with am is not invoice
            set display type is 'product'
    Case 2: with am is invoice AND aml line tax
            set display type is 'tax'
    Case 3: with am is invoice AND aml line receivable or payable,
            set display type is 'payment_term'
    Case 4: with am is invoice
            set display type is 'product'
    Case 5: with aml is an accounting transaction occurring
            set display type is 'product'
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line
        SET display_type = 'product'
        WHERE id IN (
            SELECT aml.id
            FROM account_move_line AS aml
            LEFT JOIN account_move AS am ON am.id = aml.move_id
            WHERE aml.display_type IS NULL AND
                am.move_type NOT IN (
                    'in_invoice', 'in_refund',
                    'out_invoice', 'out_refund'
                )
        )
        """,
    )

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line
        SET display_type = 'tax'
        WHERE id IN (
            SELECT aml.id
            FROM account_move_line AS aml
            INNER JOIN account_tax AS act ON act.id = aml.tax_line_id
            LEFT JOIN account_move AS am ON am.id = aml.move_id
            WHERE aml.display_type IS NULL AND
                am.move_type IN (
                    'in_invoice', 'in_refund',
                    'out_invoice', 'out_refund'
                )
        )
        """,
    )

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line
        SET display_type = 'payment_term'
        WHERE id IN (
            SELECT aml.id
            FROM account_move_line AS aml
            LEFT JOIN account_move AS am ON am.id = aml.move_id
            LEFT JOIN account_account AS acc ON acc.id = aml.account_id
            WHERE aml.display_type IS NULL AND
                am.move_type IN (
                    'in_invoice', 'in_refund',
                    'out_invoice', 'out_refund'
                ) AND
                acc.account_type IN (
                    'asset_receivable', 'liability_payable'
            )
        )
        """,
    )

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line
        SET display_type = 'product'
        WHERE id IN (
            SELECT aml.id
            FROM account_move_line AS aml
            LEFT JOIN account_move AS am ON am.id = aml.move_id
            WHERE aml.display_type IS NULL AND
                am.move_type IN (
                    'in_invoice', 'in_refund',
                    'out_invoice', 'out_refund'
                )
        )
        """,
    )

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line
        SET display_type = 'product'
        WHERE id IN (
            SELECT aml.id
            FROM account_move_line AS aml
            WHERE aml.display_type IS NULL AND (
                    aml.balance <> 0 OR
                    aml.account_id IS NOT NULL
                )
        )
        """,
    )


def _account_move_auto_post_boolean_to_selection(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_move
        ALTER COLUMN auto_post type character varying;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move AS am
        SET auto_post =
        CASE
            WHEN auto_post = 'true' THEN 'at_date'
            ELSE 'no'
        END;
        """,
    )


def _account_analytic_distribution_model_generate(env):
    if not (
        openupgrade.column_exists(
            env.cr, "account_analytic_distribution_model", "partner_id"
        )
        and openupgrade.column_exists(
            env.cr, "account_analytic_distribution_model", "product_id"
        )
        and openupgrade.column_exists(
            env.cr, "account_analytic_distribution_model", "company_id"
        )
    ):
        openupgrade.add_fields(
            env,
            [
                (
                    "partner_id",
                    "account.analytic.distribution.model",
                    "account_analytic_distribution_model",
                    "many2one",
                    False,
                    "account",
                ),
                (
                    "product_id",
                    "account.analytic.distribution.model",
                    "account_analytic_distribution_model",
                    "many2one",
                    False,
                    "account",
                ),
                (
                    "company_id",
                    "account.analytic.distribution.model",
                    "account_analytic_distribution_model",
                    "many2one",
                    False,
                    "account",
                ),
            ],
        )
    openupgrade.logged_query(
        env.cr,
        """
        WITH sub AS (
            WITH tmp AS (
                SELECT
                    id,
                    account_id,
                    percentage,
                    tag_id
                FROM
                    account_analytic_distribution
            )
            SELECT
                aad1.analytic_id AS account_analytic_account,
                aad1.partner_id AS partner_id,
                aad1.product_id AS product_id,
                aad1.company_id AS company_id,
                aad1.create_date AS create_date,
                aad1.write_date AS write_date,
                aad1.create_uid AS create_uid,
                aad1.write_uid AS write_uid,
                unnest(array_agg(tmp.tag_id)) AS tag,
                unnest(array_agg(tmp.account_id)) AS analytic_account_of_tag,
                unnest(array_agg(tmp.percentage)) AS percentage
            FROM
                account_analytic_default aad1
                JOIN account_analytic_default_account_analytic_tag_rel rel
                    ON aad1.id = rel.account_analytic_default_id
                JOIN account_analytic_tag aat
                    ON aat.id = rel.account_analytic_tag_id
                JOIN tmp
                    ON tmp.tag_id = aat.id
            GROUP BY
                aad1.analytic_id,
                aad1.partner_id,
                aad1.product_id,
                aad1.company_id,
                aad1.create_date,
                aad1.write_date,
                aad1.create_uid,
                aad1.write_uid
        )
        INSERT INTO account_analytic_distribution_model
        (partner_id,
        product_id,
        company_id,
        create_date,
        write_date,
        create_uid,
        write_uid,
        analytic_distribution)
        SELECT
            partner_id,
            product_id,
            company_id,
            create_date,
            write_date,
            create_uid,
            write_uid,
            jsonb_object_agg(analytic_account_of_tag::text, percentage) AS analytic_distribution
        FROM
            sub
        GROUP BY
            partner_id,
            product_id,
            company_id,
            create_date,
            write_date,
            create_uid,
            write_uid;
    """,
    )


def _aml_fast_fill_analytic_distribution(env):
    """
    take all the move lines, if have an analytic accounting account, it's 100%
    combined with the analytic distribution of account analytic tag
    then sum them together by analytic account
    """
    if not openupgrade.column_exists(
        env.cr, "account_move_line", "analytic_distribution"
    ):
        openupgrade.logged_query(
            env.cr,
            """
            ALTER TABLE account_move_line
            ADD COLUMN IF NOT EXISTS analytic_distribution jsonb;
            """,
        )
    openupgrade.logged_query(
        env.cr,
        """
        WITH distribution_data AS (
            WITH sub AS (
                SELECT
                    all_line_data.move_line_id,
                    all_line_data.analytic_account_id,
                    SUM(all_line_data.percentage) AS percentage
                FROM (
                    SELECT
                        move_line.id AS move_line_id,
                        account.id AS analytic_account_id,
                        100 AS percentage
                    FROM account_move_line move_line
                    JOIN account_analytic_account account
                        ON account.id = move_line.analytic_account_id
                    WHERE move_line.analytic_account_id IS NOT NULL

                    UNION ALL

                    SELECT
                        move_line.id AS move_line_id,
                        dist.account_id AS analytic_account_id,
                        dist.percentage AS percentage
                    FROM account_move_line move_line
                    JOIN account_analytic_tag_account_move_line_rel tag_rel
                        ON tag_rel.account_move_line_id = move_line.id
                    JOIN account_analytic_distribution dist
                        ON dist.tag_id = tag_rel.account_analytic_tag_id
                ) AS all_line_data
                GROUP BY all_line_data.move_line_id, all_line_data.analytic_account_id
            )
            SELECT sub.move_line_id,
            jsonb_object_agg(sub.analytic_account_id::text, sub.percentage)
                AS analytic_distribution
            FROM sub
            GROUP BY sub.move_line_id
        )
        UPDATE account_move_line move_line
        SET analytic_distribution = dist.analytic_distribution
        FROM distribution_data dist WHERE move_line.id = dist.move_line_id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _fields_renames)
    openupgrade.rename_models(env.cr, _models_renames)
    openupgrade.rename_tables(env.cr, _tables_renames)
    _fast_fill_account_account_type(env, "account.account", "account_account")
    _fast_fill_account_account_type(
        env, "account.account.template", "account_account_template"
    )
    _delete_sql_constraints(env)
    _account_analytic_line_fast_fill_journal_id(env)
    _account_bank_statement_line_fast_fill_internal_index(env)
    _account_bank_statement_fast_fill_first_line_index(env)
    _account_bank_statement_fast_fill_is_complete(env)
    _account_move_fast_fill_display_type(env)
    _account_move_auto_post_boolean_to_selection(env)
    _account_payment_fast_fill_amount_company_currency_signed(env)
    _account_analytic_distribution_model_generate(env)
    _aml_fast_fill_analytic_distribution(env)
