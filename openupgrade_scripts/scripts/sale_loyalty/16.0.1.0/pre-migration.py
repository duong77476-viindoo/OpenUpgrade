from openupgradelib import openupgrade

_rename_xmlids = [
    (
        "sale_coupon.access_applicability_manager",
        "sale_loyalty.access_applicability_manager",
    ),
    (
        "sale_coupon.access_applicability_salesman",
        "sale_loyalty.access_applicability_salesman",
    ),
    (
        "sale_coupon.access_coupon_manager",
        "sale_loyalty.access_coupon_manager",
    ),
    (
        "sale_coupon.access_coupon_salesman",
        "sale_loyalty.access_coupon_salesman",
    ),
    (
        "sale_coupon.access_program_manager",
        "sale_loyalty.access_program_manager",
    ),
    (
        "sale_coupon.access_program_salesman",
        "sale_loyalty.access_program_salesman",
    ),
    (
        "sale_coupon.access_reward_manager",
        "sale_loyalty.access_reward_manager",
    ),
    (
        "sale_coupon.access_reward_salesman",
        "sale_loyalty.access_reward_salesman",
    ),
    (
        "sale_coupon.access_sale_coupon_apply_code",
        "sale_loyalty.access_sale_coupon_apply_code",
    ),
    (
        "sale_coupon.access_sale_coupon_generate",
        "pos_loyalty.access_sale_coupon_generate",
    ),
]


def _fill_sale_order_line_coupon_id(env):
    if not openupgrade.table_exists(env.cr, "gift_card"):
        # Need to make sure gift_card module
        # has been installed in v15
        return
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE sale_order_line
          ADD COLUMN IF NOT EXISTS coupon_id INTEGER""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order_line so_line
           SET coupon_id = lcard.id
        FROM gift_card gcard
        JOIN loyalty_card lcard ON gcard.id = lcard.old_gift_card_id
        WHERE so_line.id = gcard.buy_line_id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _rename_xmlids)
    _fill_sale_order_line_coupon_id(env)
