"""Phase 8 synthetic data generation service using metadata workbooks."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from random import Random
from typing import Any
from uuid import uuid4

from src.schemas.synthetic import SyntheticVolumeConfig
from src.services.metadata_layer import EnterpriseMetadataService


class SyntheticDataService:
    """Generate realistic synthetic customer ecosystems using metadata definitions."""

    DATASET_KEYS = [
        "customer_data",
        "subscription_data",
        "household_data",
        "revenue_data",
        "interaction_history",
        "scores",
        "channel_responses",
    ]

    def __init__(self, metadata_service: EnterpriseMetadataService | None = None) -> None:
        self.metadata_service = metadata_service or EnterpriseMetadataService()

    def get_generation_template(self) -> dict[str, Any]:
        default_volume = SyntheticVolumeConfig()
        return {
            "supported_entities": list(self.DATASET_KEYS),
            "default_volume": default_volume.model_dump(),
            "override_keys": list(self.DATASET_KEYS),
            "metadata_inputs": ["data_dictionary_path", "database_model_path"],
        }

    def generate_dataset(
        self,
        volume: SyntheticVolumeConfig,
        random_seed: int | None = None,
        include_records: bool = False,
        max_inline_records_per_dataset: int = 200,
        data_dictionary_path: str | None = None,
        database_model_path: str | None = None,
    ) -> dict[str, Any]:
        rng = Random(random_seed)
        generated_at = datetime.now(UTC)

        data_dictionary = self.metadata_service.parse_data_dictionary(file_path=data_dictionary_path)
        database_model = self.metadata_service.parse_database_model(file_path=database_model_path)
        table_index = self._build_table_index(data_dictionary, database_model)

        resolved_tables = {
            "customer_data": self._resolve_table(table_index, ["customer", "member", "cust"]),
            "subscription_data": self._resolve_table(table_index, ["subscription", "plan", "product"]),
            "household_data": self._resolve_table(table_index, ["household", "home", "family"]),
            "revenue_data": self._resolve_table(table_index, ["revenue", "billing", "payment", "invoice"]),
            "interaction_history": self._resolve_table(table_index, ["interaction", "contact", "event", "touch"]),
            "scores": self._resolve_table(table_index, ["score", "propensity", "churn", "clv"]),
            "channel_responses": self._resolve_table(table_index, ["response", "channel", "engagement"]),
        }

        customer_count = volume.record_overrides.get("customer_data", volume.customer_count)
        household_count = volume.record_overrides.get(
            "household_data",
            max(1, round(customer_count * volume.household_coverage_ratio)),
        )
        subscription_count = volume.record_overrides.get(
            "subscription_data",
            max(1, round(customer_count * volume.avg_subscriptions_per_customer)),
        )
        interaction_count = volume.record_overrides.get(
            "interaction_history",
            customer_count * volume.avg_interactions_per_customer,
        )
        response_count = volume.record_overrides.get(
            "channel_responses",
            max(0, round(interaction_count * volume.channel_response_rate)),
        )
        score_count = volume.record_overrides.get("scores", customer_count)
        revenue_count = volume.record_overrides.get("revenue_data", subscription_count)

        households = self._generate_households(household_count, rng, generated_at)
        customers = self._generate_customers(customer_count, households, rng, generated_at)
        subscriptions = self._generate_subscriptions(subscription_count, customers, rng, generated_at)
        interactions = self._generate_interactions(interaction_count, customers, rng, generated_at)
        responses = self._generate_channel_responses(
            response_count,
            interactions,
            customers,
            volume.conversion_rate,
            rng,
            generated_at,
        )
        scores = self._generate_scores(score_count, customers, rng, generated_at)
        revenue = self._generate_revenue(revenue_count, subscriptions, customers, rng, generated_at)

        raw_records = {
            "customer_data": self._project_rows(
                "customer_data",
                customers,
                resolved_tables,
                table_index,
                rng,
            ),
            "subscription_data": self._project_rows(
                "subscription_data",
                subscriptions,
                resolved_tables,
                table_index,
                rng,
            ),
            "household_data": self._project_rows(
                "household_data",
                households,
                resolved_tables,
                table_index,
                rng,
            ),
            "revenue_data": self._project_rows(
                "revenue_data",
                revenue,
                resolved_tables,
                table_index,
                rng,
            ),
            "interaction_history": self._project_rows(
                "interaction_history",
                interactions,
                resolved_tables,
                table_index,
                rng,
            ),
            "scores": self._project_rows(
                "scores",
                scores,
                resolved_tables,
                table_index,
                rng,
            ),
            "channel_responses": self._project_rows(
                "channel_responses",
                responses,
                resolved_tables,
                table_index,
                rng,
            ),
        }

        samples = {key: rows[: min(5, len(rows))] for key, rows in raw_records.items()}
        records = None
        truncated_records: dict[str, bool] = {key: False for key in self.DATASET_KEYS}

        if include_records:
            records = {}
            for key, rows in raw_records.items():
                if len(rows) > max_inline_records_per_dataset:
                    records[key] = rows[:max_inline_records_per_dataset]
                    truncated_records[key] = True
                else:
                    records[key] = rows

        return {
            "dataset_id": f"syn_{uuid4().hex[:12]}",
            "generated_at": generated_at,
            "metadata_sources": {
                "data_dictionary": data_dictionary.get("file_path", "unknown"),
                "database_model": database_model.get("file_path", "unknown"),
            },
            "resolved_tables": resolved_tables,
            "volumes": {key: len(raw_records[key]) for key in self.DATASET_KEYS},
            "truncated_records": truncated_records,
            "samples": samples,
            "records": records,
        }

    def _build_table_index(
        self,
        data_dictionary: dict[str, Any],
        database_model: dict[str, Any],
    ) -> dict[str, dict[str, str | None]]:
        table_index: dict[str, dict[str, str | None]] = {}
        for metadata in (database_model, data_dictionary):
            for table in metadata.get("tables", []):
                table_name = str(table.get("name", "")).strip().lower()
                if not table_name:
                    continue
                columns = table_index.setdefault(table_name, {})
                for col in table.get("columns", []):
                    col_name = str(col.get("name", "")).strip().lower()
                    if not col_name:
                        continue
                    columns.setdefault(col_name, col.get("data_type"))
        return table_index

    def _resolve_table(self, table_index: dict[str, dict[str, str | None]], keywords: list[str]) -> str | None:
        best: tuple[int, str] | None = None
        for table_name in table_index:
            score = 0
            for keyword in keywords:
                if keyword in table_name:
                    score += len(keyword)
            if score <= 0:
                continue
            if best is None or score > best[0]:
                best = (score, table_name)
        return best[1] if best else None

    def _project_rows(
        self,
        dataset_key: str,
        rows: list[dict[str, Any]],
        resolved_tables: dict[str, str | None],
        table_index: dict[str, dict[str, str | None]],
        rng: Random,
    ) -> list[dict[str, Any]]:
        table_name = resolved_tables.get(dataset_key)
        if not table_name or table_name not in table_index:
            return rows

        columns = table_index[table_name]
        projected_rows: list[dict[str, Any]] = []
        for row in rows:
            projected_rows.append(
                {
                    col: self._value_for_column(col, data_type, row, rng)
                    for col, data_type in columns.items()
                }
            )
        return projected_rows

    def _value_for_column(
        self,
        column_name: str,
        data_type: str | None,
        row: dict[str, Any],
        rng: Random,
    ) -> Any:
        if column_name in row:
            return row[column_name]

        compact = column_name.replace("_", "")
        for key, value in row.items():
            if key.replace("_", "") == compact:
                return value

        lowered = column_name.lower()
        if "customer_id" in lowered:
            return row.get("customer_id")
        if "household_id" in lowered:
            return row.get("household_id")
        if "subscription_id" in lowered:
            return row.get("subscription_id")
        if "interaction_id" in lowered:
            return row.get("interaction_id")
        if "revenue_id" in lowered:
            return row.get("revenue_id")
        if "email" in lowered:
            return row.get("email")
        if "name" in lowered:
            return row.get("first_name") or row.get("last_name") or "Unknown"

        inferred_type = (data_type or "").lower()
        if any(x in inferred_type for x in ["int", "number", "numeric"]):
            return rng.randint(0, 9999)
        if any(x in inferred_type for x in ["float", "decimal", "double"]):
            return round(rng.uniform(0, 1000), 2)
        if "bool" in inferred_type:
            return bool(rng.randint(0, 1))
        if "date" in inferred_type or "time" in inferred_type:
            return datetime.now(UTC).isoformat()
        return None

    def _generate_households(self, count: int, rng: Random, now: datetime) -> list[dict[str, Any]]:
        income_bands = ["low", "lower_mid", "upper_mid", "high", "affluent"]
        states = ["CA", "TX", "NY", "FL", "WA", "IL"]
        cities = ["Los Angeles", "Houston", "New York", "Miami", "Seattle", "Chicago"]
        households: list[dict[str, Any]] = []
        for idx in range(1, count + 1):
            households.append(
                {
                    "household_id": f"H{idx:07d}",
                    "household_size": rng.randint(1, 6),
                    "income_band": rng.choices(income_bands, weights=[12, 26, 34, 20, 8], k=1)[0],
                    "city": rng.choice(cities),
                    "state": rng.choice(states),
                    "digital_affinity": round(rng.uniform(0.1, 0.98), 3),
                    "created_at": (now - timedelta(days=rng.randint(30, 3000))).isoformat(),
                }
            )
        return households

    def _generate_customers(
        self,
        count: int,
        households: list[dict[str, Any]],
        rng: Random,
        now: datetime,
    ) -> list[dict[str, Any]]:
        first_names = ["Liam", "Olivia", "Noah", "Emma", "Ava", "Sophia", "Ethan", "Mia"]
        last_names = ["Smith", "Johnson", "Brown", "Davis", "Wilson", "Taylor", "Thomas", "Moore"]
        segments = ["value_seekers", "loyalists", "growth", "at_risk", "premium"]
        customers: list[dict[str, Any]] = []

        household_ids = [household["household_id"] for household in households]
        for idx in range(1, count + 1):
            first_name = rng.choice(first_names)
            last_name = rng.choice(last_names)
            tenure_months = rng.randint(1, 120)
            age = rng.randint(18, 84)
            dob = now.date() - timedelta(days=age * 365 + rng.randint(0, 364))
            customer_id = f"C{idx:07d}"
            customers.append(
                {
                    "customer_id": customer_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": f"{first_name.lower()}.{last_name.lower()}{idx}@example.com",
                    "date_of_birth": dob.isoformat(),
                    "age": age,
                    "tenure_months": tenure_months,
                    "segment": rng.choices(segments, weights=[24, 22, 19, 17, 18], k=1)[0],
                    "household_id": rng.choice(household_ids),
                    "created_at": (now - timedelta(days=tenure_months * 30 + rng.randint(0, 120))).isoformat(),
                    "is_active": rng.random() > 0.07,
                }
            )
        return customers

    def _generate_subscriptions(
        self,
        count: int,
        customers: list[dict[str, Any]],
        rng: Random,
        now: datetime,
    ) -> list[dict[str, Any]]:
        plans = ["basic", "plus", "pro", "family", "enterprise"]
        statuses = ["active", "paused", "cancelled", "trial"]
        products = ["streaming", "mobile", "fiber", "bundle", "premium_content"]
        subscriptions: list[dict[str, Any]] = []
        for idx in range(1, count + 1):
            customer = rng.choice(customers)
            start_date = now.date() - timedelta(days=rng.randint(5, 900))
            status = rng.choices(statuses, weights=[70, 9, 14, 7], k=1)[0]
            end_date = None
            if status == "cancelled":
                end_date = (start_date + timedelta(days=rng.randint(20, 500))).isoformat()
            subscriptions.append(
                {
                    "subscription_id": f"S{idx:07d}",
                    "customer_id": customer["customer_id"],
                    "product_name": rng.choice(products),
                    "plan_tier": rng.choice(plans),
                    "status": status,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date,
                    "monthly_fee": round(rng.uniform(9.99, 199.99), 2),
                    "auto_renew": status in {"active", "paused"} and rng.random() > 0.15,
                }
            )
        return subscriptions

    def _generate_interactions(
        self,
        count: int,
        customers: list[dict[str, Any]],
        rng: Random,
        now: datetime,
    ) -> list[dict[str, Any]]:
        channels = ["email", "sms", "push", "ivr", "app", "web", "call_center"]
        events = ["delivered", "opened", "clicked", "viewed", "called", "ignored", "bounced"]
        interactions: list[dict[str, Any]] = []
        for idx in range(1, count + 1):
            customer = rng.choice(customers)
            timestamp = now - timedelta(days=rng.randint(0, 365), hours=rng.randint(0, 23), minutes=rng.randint(0, 59))
            interactions.append(
                {
                    "interaction_id": f"I{idx:08d}",
                    "customer_id": customer["customer_id"],
                    "channel": rng.choice(channels),
                    "event_type": rng.choice(events),
                    "event_timestamp": timestamp.isoformat(),
                    "campaign_id": rng.randint(1000, 9999),
                    "response_latency_hours": round(rng.uniform(0.0, 96.0), 2),
                }
            )
        return interactions

    def _generate_channel_responses(
        self,
        count: int,
        interactions: list[dict[str, Any]],
        customers: list[dict[str, Any]],
        conversion_rate: float,
        rng: Random,
        now: datetime,
    ) -> list[dict[str, Any]]:
        if count <= 0:
            return []

        responses: list[dict[str, Any]] = []
        interaction_pool = interactions[:]
        rng.shuffle(interaction_pool)

        if not interaction_pool:
            for idx in range(1, count + 1):
                customer = rng.choice(customers)
                converted = rng.random() < conversion_rate
                responses.append(
                    {
                        "response_id": f"R{idx:08d}",
                        "customer_id": customer["customer_id"],
                        "interaction_id": None,
                        "channel": rng.choice(["email", "sms", "push"]),
                        "responded": True,
                        "conversion": converted,
                        "conversion_value": round(rng.uniform(0, 250), 2) if converted else 0.0,
                        "response_timestamp": (now - timedelta(days=rng.randint(0, 365))).isoformat(),
                    }
                )
            return responses

        for idx in range(1, count + 1):
            interaction = interaction_pool[(idx - 1) % len(interaction_pool)]
            converted = rng.random() < conversion_rate
            responses.append(
                {
                    "response_id": f"R{idx:08d}",
                    "customer_id": interaction["customer_id"],
                    "interaction_id": interaction["interaction_id"],
                    "channel": interaction["channel"],
                    "responded": True,
                    "conversion": converted,
                    "conversion_value": round(rng.uniform(5.0, 500.0), 2) if converted else 0.0,
                    "response_timestamp": (now - timedelta(days=rng.randint(0, 365))).isoformat(),
                }
            )
        return responses

    def _generate_scores(
        self,
        count: int,
        customers: list[dict[str, Any]],
        rng: Random,
        now: datetime,
    ) -> list[dict[str, Any]]:
        scores: list[dict[str, Any]] = []
        for idx in range(1, count + 1):
            customer = customers[(idx - 1) % len(customers)]
            scores.append(
                {
                    "score_id": f"SC{idx:08d}",
                    "customer_id": customer["customer_id"],
                    "churn_risk_score": round(rng.uniform(0.01, 0.99), 4),
                    "propensity_to_buy_score": round(rng.uniform(0.01, 0.99), 4),
                    "customer_lifetime_value_score": round(rng.uniform(50, 6000), 2),
                    "next_best_offer_score": round(rng.uniform(0.01, 0.99), 4),
                    "last_scored_at": (now - timedelta(days=rng.randint(0, 60))).isoformat(),
                }
            )
        return scores

    def _generate_revenue(
        self,
        count: int,
        subscriptions: list[dict[str, Any]],
        customers: list[dict[str, Any]],
        rng: Random,
        now: datetime,
    ) -> list[dict[str, Any]]:
        revenue_rows: list[dict[str, Any]] = []
        for idx in range(1, count + 1):
            subscription = subscriptions[(idx - 1) % len(subscriptions)] if subscriptions else None
            customer_id = subscription["customer_id"] if subscription else rng.choice(customers)["customer_id"]
            amount = round(rng.uniform(8.0, 250.0), 2)
            revenue_rows.append(
                {
                    "revenue_id": f"REV{idx:08d}",
                    "customer_id": customer_id,
                    "subscription_id": subscription["subscription_id"] if subscription else None,
                    "amount": amount,
                    "currency": "USD",
                    "bill_date": (now.date() - timedelta(days=rng.randint(0, 540))).isoformat(),
                    "payment_status": rng.choices(["paid", "pending", "failed"], weights=[88, 9, 3], k=1)[0],
                    "discount_amount": round(amount * rng.choice([0.0, 0.05, 0.1, 0.15]), 2),
                }
            )
        return revenue_rows
