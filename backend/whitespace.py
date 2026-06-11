"""
Whitespace / upsell analysis engine.

For each customer: what Onyx products do they own, what do *similar* customers
(same industry, then same tier) own that they don't, and what would closing
that gap be worth — rolling up to an ultimate ARR goal per account and for
the portfolio's largest clients.
"""

from statistics import median

from backend.database import fetchall


def _load():
    products  = fetchall("SELECT * FROM products ORDER BY id")
    ownership = fetchall("SELECT * FROM customer_products")
    customers = fetchall("SELECT * FROM customers")
    owned_by_customer = {}
    for row in ownership:
        owned_by_customer.setdefault(row["customer_id"], {})[row["product_id"]] = row
    return products, owned_by_customer, customers


def _peers(customer, customers):
    """Similar clients: same industry first; pad with same tier if thin."""
    peers = [c for c in customers
             if c["id"] != customer["id"] and c["industry"] == customer["industry"]]
    if len(peers) < 4:
        peers += [c for c in customers
                  if c["id"] != customer["id"]
                  and c["customer_tier"] == customer["customer_tier"]
                  and c not in peers]
    return peers


def _estimate_price(product_id, customer, owned_by_customer, peers, products_by_id):
    """Estimated ARR for an unowned product: median of what peers pay for it,
    scaled mildly by relative company size; falls back to tier-adjusted list."""
    peer_prices = [
        owned_by_customer[p["id"]][product_id]["arr"]
        for p in peers
        if product_id in owned_by_customer.get(p["id"], {})
    ]
    if peer_prices:
        base = median(peer_prices)
        peer_emp = median([p["employee_count"] for p in peers]) or 1
        scale = max(0.7, min(1.6, customer["employee_count"] / peer_emp))
        return int(base * scale / 1000) * 1000
    mult = {"Mid-Market": 1.0, "Enterprise": 1.6, "Strategic": 2.6}.get(customer["customer_tier"], 1.0)
    return int(products_by_id[product_id]["base_price"] * mult / 1000) * 1000


def customer_whitespace(customer_id: int) -> dict:
    """Owned products + ranked upsell opportunities with an ARR goal."""
    products, owned_by_customer, customers = _load()
    products_by_id = {p["id"]: p for p in products}
    customer = next((c for c in customers if c["id"] == customer_id), None)
    if not customer:
        return {}

    owned = owned_by_customer.get(customer_id, {})
    peers = _peers(customer, customers)
    n_peers = max(len(peers), 1)

    owned_list = [
        {
            "product_id": pid,
            "product_name": products_by_id[pid]["name"],
            "category": products_by_id[pid]["category"],
            "description": products_by_id[pid]["description"],
            "arr": row["arr"],
            "purchased_date": row["purchased_date"],
        }
        for pid, row in sorted(owned.items(), key=lambda kv: -kv[1]["arr"])
    ]

    opportunities = []
    for p in products:
        if p["id"] in owned:
            continue
        peer_owners = [q for q in peers if p["id"] in owned_by_customer.get(q["id"], {})]
        penetration = len(peer_owners) / n_peers
        est_arr = _estimate_price(p["id"], customer, owned_by_customer, peers, products_by_id)
        # Score: how common among lookalikes × account's upsell appetite
        score = penetration * (0.5 + (customer["upsell_likelihood"] or 0.3))
        opportunities.append({
            "product_id": p["id"],
            "product_name": p["name"],
            "category": p["category"],
            "description": p["description"],
            "estimated_arr": est_arr,
            "peer_penetration_pct": round(penetration * 100),
            "peer_examples": [q["name"] for q in
                              sorted(peer_owners, key=lambda q: -q["arr"])[:3]],
            "score": round(score, 3),
        })
    opportunities.sort(key=lambda o: (-o["score"], -o["estimated_arr"]))

    recommended = [o for o in opportunities if o["peer_penetration_pct"] >= 25][:3]
    whitespace_arr = sum(o["estimated_arr"] for o in recommended)

    return {
        "customer_id": customer_id,
        "customer_name": customer["name"],
        "industry": customer["industry"],
        "customer_tier": customer["customer_tier"],
        "current_arr": customer["arr"],
        "upsell_likelihood": customer["upsell_likelihood"],
        "peer_count": len(peers),
        "owned_products": owned_list,
        "opportunities": opportunities,
        "recommended": recommended,
        "whitespace_arr": whitespace_arr,
        "arr_goal": customer["arr"] + whitespace_arr,
    }


def portfolio_whitespace(top_n: int = 12) -> dict:
    """Product penetration matrix + ARR goals for the largest clients."""
    products, owned_by_customer, customers = _load()
    largest = sorted(customers, key=lambda c: -c["arr"])[:top_n]

    rows = []
    total_current, total_goal = 0, 0
    for c in largest:
        ws = customer_whitespace(c["id"])
        cells = []
        owned_ids = {o["product_id"] for o in ws["owned_products"]}
        rec_ids = {o["product_id"]: o for o in ws["recommended"]}
        for p in products:
            if p["id"] in owned_ids:
                arr = next(o["arr"] for o in ws["owned_products"] if o["product_id"] == p["id"])
                cells.append({"product_id": p["id"], "state": "owned", "arr": arr})
            elif p["id"] in rec_ids:
                cells.append({"product_id": p["id"], "state": "recommended",
                              "arr": rec_ids[p["id"]]["estimated_arr"],
                              "peer_penetration_pct": rec_ids[p["id"]]["peer_penetration_pct"]})
            else:
                cells.append({"product_id": p["id"], "state": "none", "arr": 0})
        rows.append({
            "customer_id": c["id"],
            "customer_name": c["name"],
            "industry": c["industry"],
            "customer_tier": c["customer_tier"],
            "risk_level": c["risk_level"],
            "health_score": c["health_score"],
            "current_arr": c["arr"],
            "whitespace_arr": ws["whitespace_arr"],
            "arr_goal": ws["arr_goal"],
            "recommended": ws["recommended"],
            "cells": cells,
        })
        total_current += c["arr"]
        total_goal += ws["arr_goal"]

    return {
        "products": products,
        "rows": rows,
        "total_current_arr": total_current,
        "total_whitespace_arr": total_goal - total_current,
        "total_arr_goal": total_goal,
        "growth_pct": round((total_goal / total_current - 1) * 100, 1) if total_current else 0,
    }
