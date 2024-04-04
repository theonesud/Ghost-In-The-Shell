import itertools

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import String, cast, extract, func, select

from api.helper import (
    check_if_role_exists,
    get_user_from_token,
)
from config import logger
from model import db
from model.db import get_session

router = APIRouter(prefix="/sales")


def create_query(table, filters, ean_filter=None, has_channel=False, is_sales=False):
    if is_sales:
        query = select(table.date, table.ean, table.qty, table.sp_per_pc)
    else:
        query = select(table.year, table.month, table.ean, table.qty)
    if has_channel:
        query = query.join(db.Channel, table.channel_id == db.Channel.id)
        query = query.filter(db.Channel.name.in_(filters["channels"]))
    if ean_filter:
        query = query.where(table.ean.in_(ean_filter))
    if is_sales:
        query = query.filter(
            func.concat(
                extract("year", table.date),
                "-",
                func.lpad(cast(extract("month", table.date), String), 2, "0"),
            ).between(filters["month_start"], filters["month_end"])
        )
    else:
        query = query.where(
            func.concat(
                table.year, "-", func.lpad(cast(table.month, String), 2, "0")
            ).between(filters["month_start"], filters["month_end"])
        )
    return query


def make_date(df):
    df["date"] = pd.to_datetime(
        df["year"].astype(str) + "-" + df["month"].astype(str)
    ).dt.strftime("%Y-%m")
    df = df.drop(columns=["year", "month"])
    return df


async def run_pdp_queries(product_id, filters):
    ean_size_map = select(db.Sizes.ean, db.Sizes.standard_size).where(
        db.Sizes.product_id == product_id
    )
    async with get_session() as s:
        ean_size_map = (await s.execute(ean_size_map)).all()
    ean_filter = [i[0] for i in ean_size_map]

    wip_query = create_query(db.WIP, filters, ean_filter)
    grn_query = create_query(db.GRN, filters, ean_filter)
    soh_query = create_query(db.SOH, filters, ean_filter, has_channel=True)
    returns_query = create_query(db.Returns, filters, ean_filter, has_channel=True)
    sales_query = create_query(
        db.Sales, filters, ean_filter, has_channel=True, is_sales=True
    )
    cost_query = select(db.Styles.cost).where(db.Styles.product_id == product_id)
    async with get_session() as s:
        wip = pd.DataFrame(
            (await s.execute(wip_query)).all(), columns=["year", "month", "ean", "qty"]
        )
        grn = pd.DataFrame(
            (await s.execute(grn_query)).all(), columns=["year", "month", "ean", "qty"]
        )
        soh = pd.DataFrame(
            (await s.execute(soh_query)).all(), columns=["year", "month", "ean", "qty"]
        )
        returns = pd.DataFrame(
            (await s.execute(returns_query)).all(),
            columns=["year", "month", "ean", "qty"],
        )
        sales = pd.DataFrame(
            (await s.execute(sales_query)).all(),
            columns=["date", "ean", "qty", "sp_per_pc"],
        )
        cost = (await s.execute(cost_query)).first()[0]

    all_months = pd.date_range(
        start=f'{filters["month_start"]}', end=f'{filters["month_end"]}', freq="MS"
    ).strftime("%Y-%m")
    index = pd.MultiIndex.from_tuples(
        list(itertools.product(all_months, [x[1] for x in ean_size_map])),
        names=["date", "ean"],
    )
    empty_df = pd.DataFrame(index=index)

    sales["revenue"] = sales["qty"] * sales["sp_per_pc"]
    sales["date"] = pd.to_datetime(sales["date"]).dt.strftime("%Y-%m")

    def group(df):
        if not len(df):
            return df
        df = df.groupby(["date", "ean"]).sum()
        df.reset_index(inplace=True)
        return df

    def fill_gaps(df):
        df["ean"] = df["ean"].map(dict(ean_size_map))
        df.set_index(["date", "ean"], inplace=True)
        temp = empty_df.copy()
        temp = temp.merge(df, on=["date", "ean"], how="left")
        temp.reset_index(inplace=True)
        temp.fillna(0, inplace=True)
        return temp

    return (
        fill_gaps(group(make_date(wip))),
        fill_gaps(group(make_date(grn))),
        fill_gaps(group(make_date(soh))),
        fill_gaps(group(make_date(returns))),
        fill_gaps(group(sales)),
        cost,
    )


def make_json(df, index_key="ean"):
    df.reset_index(inplace=True)
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.fillna(0, inplace=True)
    df = df.round(2)

    if index_key in df.columns:
        df = df[["date", index_key, "qty"]]
        df = df.pivot(index="date", columns=index_key, values="qty")
        df_dict = df.to_dict("index")
        resp = list(df_dict.values())
        for i, date in enumerate(df_dict.keys()):
            resp[i]["name"] = date
    else:
        # for instock %
        resp = df.to_dict("records")
        resp = [{"name": d["date"], "instock": d["instock"]} for d in resp]

    return resp


def calculate_metrics(grn, soh, returns, sales, cost=None, index_key="ean"):
    returns_idx = returns.set_index(["date", index_key])
    sales_idx = sales.set_index(["date", index_key])
    soh_idx = soh.set_index(["date", index_key])
    grn_idx = grn.set_index(["date", index_key])

    rate_of_sales = sales.copy()
    rate_of_sales["qty"] = sales["qty"] / 30

    sale_revenue = sales.copy()
    sale_revenue.drop(columns=["qty"], inplace=True)
    sale_revenue.rename(columns={"revenue": "qty"}, inplace=True)
    sale_revenue_idx = sale_revenue.set_index(["date", index_key])

    rate_of_returns = returns.copy()
    rate_of_returns["qty"] = returns["qty"] / 30

    return_ratio = (returns_idx * 100) / sales_idx

    net_sales = sales_idx - returns_idx

    if index_key == "ean":
        sale_cost_idx = sales_idx.copy()
        sale_cost_idx.fillna(0, inplace=True)
        sale_cost_idx["qty"] = sales_idx["qty"] * cost
        sale_profit = sale_revenue_idx - sale_cost_idx

        instock = soh.copy()
        instock["instock"] = instock["qty"] > 0
        instock = instock.groupby("date")["instock"].mean() * 100
        instock = instock.to_frame(name="instock")
    else:
        sale_profit = None
        instock = None

    stock_turn_ratio = (sales_idx * 100) / soh_idx

    sell_through_ratio = (sales_idx * 100) / grn_idx

    return (
        rate_of_sales,
        sale_revenue,
        rate_of_returns,
        return_ratio,
        net_sales,
        sale_profit,
        instock,
        stock_turn_ratio,
        sell_through_ratio,
    )


@router.post("/{product_id}")
async def get_sales_data(
    product_id: str, filters: dict = None, user=Depends(get_user_from_token)
):
    if filters is None:
        filters = {}
    if not check_if_role_exists(user["department"]["roles"], "sales analytics", "read"):
        raise HTTPException(
            403, "You don't have permission to see sales analysis chart"
        )
    logger.info(f"{user['name']} is trying to see sales analytics of {product_id}")

    (
        wip,
        grn,
        soh,
        returns,
        sales,
        cost,
    ) = await run_pdp_queries(product_id, filters)

    (
        rate_of_sales,
        revenue,
        rate_of_returns,
        return_ratio,
        net_sales,
        sale_profit,
        instock,
        stock_turn_ratio,
        sell_through_ratio,
    ) = calculate_metrics(
        grn,
        soh,
        returns,
        sales,
        cost,
    )

    return {
        "msg": "Sales data fetched successfully",
        "info": {
            # sales
            "sales": make_json(sales),
            "rate_of_sales": make_json(rate_of_sales),
            "sale_revenue": make_json(revenue),
            "sale_profit": make_json(sale_profit),
            # returns
            "returns": make_json(returns),
            "rate_of_return": make_json(rate_of_returns),
            # sales / return
            "return_ratio": make_json(return_ratio),
            # sales - returns
            "net_sales": make_json(net_sales),
            # soh
            "soh": make_json(soh),
            "instock": make_json(instock),
            "stock_turn": make_json(stock_turn_ratio),
            # grn
            "grn": make_json(grn),
            "sell_though": make_json(sell_through_ratio),
            # wip
            "wip": make_json(wip),
        },
    }


async def run_plp_queries(filters):
    wip_query = create_query(db.WIP, filters)
    grn_query = create_query(db.GRN, filters)
    soh_query = create_query(db.SOH, filters, has_channel=True)
    returns_query = create_query(db.Returns, filters, has_channel=True)
    sales_query = create_query(db.Sales, filters, has_channel=True, is_sales=True)
    get_ean_pid_map = select(db.Sizes.ean, db.Sizes.product_id)
    get_pid_product_map = select(db.Styles.product_id, db.Styles.product)
    get_distict_products = select(db.Styles.product).distinct()

    async with get_session() as s:
        wip = pd.DataFrame(
            (await s.execute(wip_query)).all(), columns=["year", "month", "ean", "qty"]
        )
        grn = pd.DataFrame(
            (await s.execute(grn_query)).all(), columns=["year", "month", "ean", "qty"]
        )
        soh = pd.DataFrame(
            (await s.execute(soh_query)).all(), columns=["year", "month", "ean", "qty"]
        )
        returns = pd.DataFrame(
            (await s.execute(returns_query)).all(),
            columns=["year", "month", "ean", "qty"],
        )
        sales = pd.DataFrame(
            (await s.execute(sales_query)).all(),
            columns=["date", "ean", "qty", "sp_per_pc"],
        )
        ean_pid_map = (await s.execute(get_ean_pid_map)).all()
        pid_product_map = (await s.execute(get_pid_product_map)).all()
        products = (await s.execute(get_distict_products)).all()

    def map_pids(df):
        df["pid"] = df["ean"].map(dict(ean_pid_map))
        df["product"] = df["pid"].map(dict(pid_product_map))
        return df

    wip = map_pids(wip)
    grn = map_pids(grn)
    soh = map_pids(soh)
    returns = map_pids(returns)
    sales = map_pids(sales)

    unique_pids = set()
    for df in [sales, returns]:
        unique_pids.update(df["pid"].unique())
    unique_pids = [x for x in unique_pids if isinstance(x, str)]

    async with get_session() as s:
        pid_cost_map = (
            await s.execute(
                select(db.Styles.product_id, db.Styles.cost).where(
                    db.Styles.product_id.in_(unique_pids)
                )
            )
        ).all()

    all_months = pd.date_range(
        start=f'{filters["month_start"]}', end=f'{filters["month_end"]}', freq="MS"
    ).strftime("%Y-%m")
    index = pd.MultiIndex.from_tuples(
        list(itertools.product(all_months, [x[0] for x in products])),
        names=["date", "product"],
    )
    empty_df = pd.DataFrame(index=index)

    def group(df):
        if not len(df):
            return df
        df = df.groupby(["date", "product"]).sum()
        df.reset_index(inplace=True)
        return df

    def group_pid(df):
        if not len(df):
            return df
        df = df.groupby(["date", "pid"]).sum()
        df.reset_index(inplace=True)
        return df

    def fill_gaps(df):
        df.set_index(["date", "product"], inplace=True)
        temp = empty_df.copy()
        temp = temp.merge(df, on=["date", "product"], how="left")
        temp.reset_index(inplace=True)
        temp.fillna(0, inplace=True)
        return temp

    sales["revenue"] = sales["qty"] * sales["sp_per_pc"]
    sales["date"] = pd.to_datetime(sales["date"]).dt.strftime("%Y-%m")
    sales_pid = group_pid(sales)

    sale_profit = sales_pid.copy()
    sale_profit["cost"] = sale_profit["pid"].map(dict(pid_cost_map))
    sale_profit["product"] = sale_profit["pid"].map(dict(pid_product_map))
    sale_profit["total_cost"] = sale_profit["qty"] * sale_profit["cost"]
    sale_profit["qty"] = sale_profit["revenue"] - sale_profit["total_cost"]
    sale_profit = fill_gaps(group(sale_profit))
    sale_profit = sale_profit.round(2)

    instock = soh.copy()
    instock = make_date(instock)
    instock["instock"] = instock["qty"] > 0
    instock = instock.groupby(["date", "pid"])["instock"].mean() * 100
    instock = instock.to_frame(name="qty")
    instock.reset_index(inplace=True)
    instock["product"] = instock["pid"].map(dict(pid_product_map))
    instock = instock.groupby(["date", "product"]).mean()
    instock.reset_index(inplace=True)
    instock = instock.round(2)
    instock = fill_gaps(instock)

    return (
        fill_gaps(group(make_date(wip))),
        fill_gaps(group(make_date(grn))),
        fill_gaps(group(make_date(soh))),
        fill_gaps(group(make_date(returns))),
        fill_gaps(group(sales)),
        group_pid(make_date(wip)),
        group_pid(make_date(grn)),
        group_pid(make_date(soh)),
        group_pid(make_date(returns)),
        sales_pid,
        sale_profit,
        instock,
    )


@router.post("/")
async def get_sales_overview(filters: dict = None, user=Depends(get_user_from_token)):
    if filters is None:
        filters = {}
    if not check_if_role_exists(user["department"]["roles"], "sales analytics", "read"):
        raise HTTPException(
            403, "You don't have permission to see sales analysis chart"
        )
    logger.info(f"{user['name']} is trying to see sales overview")
    (
        wip,
        grn,
        soh,
        returns,
        sales,
        wip_pid,
        grn_pid,
        soh_pid,
        returns_pid,
        sales_pid,
        sale_profit,
        instock,
    ) = await run_plp_queries(filters)
    (
        rate_of_sales,
        sale_revenue,
        rate_of_returns,
        return_ratio,
        net_sales,
        _,
        _,
        stock_turn_ratio,
        sell_through_ratio,
    ) = calculate_metrics(grn, soh, returns, sales, None, "product")

    return {
        "msg": "Sales data fetched successfully",
        "info": {
            # sales
            "sales": make_json(sales, "product"),
            "rate_of_sales": make_json(rate_of_sales, "product"),
            "sale_revenue": make_json(sale_revenue, "product"),
            "sale_profit": make_json(sale_profit, "product"),
            # returns
            "returns": make_json(returns, "product"),
            "rate_of_return": make_json(rate_of_returns, "product"),
            # sales / return
            "return_ratio": make_json(return_ratio, "product"),
            # sales - returns
            "net_sales": make_json(net_sales, "product"),
            # soh
            "soh": make_json(soh, "product"),
            "instock": make_json(instock, "product"),
            "stock_turn": make_json(stock_turn_ratio, "product"),
            # grn
            "grn": make_json(grn, "product"),
            "sell_though": make_json(sell_through_ratio, "product"),
            # wip
            "wip": make_json(wip, "product"),
            # tables
            "wip_table": wip_pid.to_dict(),
            "grn_table": grn_pid.to_dict(),
            "soh_table": soh_pid.to_dict(),
            "returns_table": returns_pid.to_dict(),
            "sales_table": sales_pid.to_dict(),
        },
    }
