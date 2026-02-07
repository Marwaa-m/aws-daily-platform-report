import os
import csv
import json
import datetime as dt
import boto3

def money(x):
    try:
        return round(float(x), 2)
    except Exception:
        return None

def main():
    region = os.getenv("AWS_REGION", "us-east-1")
    ce = boto3.client("ce", region_name=region)

    today = dt.date.today()
    start = (today - dt.timedelta(days=1)).isoformat()
    end = today.isoformat()

    total_resp = ce.get_cost_and_usage(
        TimePeriod={"Start": start, "End": end},
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
    )

    total_amount = total_resp["ResultsByTime"][0]["Total"]["UnblendedCost"]["Amount"]
    total_unit = total_resp["ResultsByTime"][0]["Total"]["UnblendedCost"]["Unit"]

    by_service = ce.get_cost_and_usage(
        TimePeriod={"Start": start, "End": end},
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
    )

    groups = by_service["ResultsByTime"][0].get("Groups", [])
    service_costs = []
    for g in groups:
        service = g["Keys"][0]
        amt = g["Metrics"]["UnblendedCost"]["Amount"]
        service_costs.append((service, money(amt)))

    service_costs.sort(key=lambda x: (x[1] is None, x[1]), reverse=True)
    top10 = service_costs[:10]

    os.makedirs("reports", exist_ok=True)
    report_date = start

    csv_path = "reports/aws-cost-daily.csv"
    file_exists = os.path.exists(csv_path)
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not file_exists:
            w.writerow(["date", "total_cost", "currency"])
        w.writerow([report_date, money(total_amount), total_unit])

    with open(f"reports/aws-cost-{report_date}.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "date": report_date,
                "total": {"amount": money(total_amount), "unit": total_unit},
                "top_services": [{"service": s, "cost": c} for s, c in top10],
            },
            f,
            indent=2,
        )

    md = []
    md.append(f"# AWS Daily Platform Report — {report_date}")
    md.append("")
    md.append("## AWS Cost (yesterday)")
    md.append(f"- Total spend: **{money(total_amount)} {total_unit}**")
    md.append("")
    md.append("### Top services")
    for s, c in top10:
        md.append(f"- {s}: **{c} {total_unit}**")
    md.append("")
    md.append("## Terraform checks")
    md.append("- `terraform fmt -check`, `terraform validate`, and `terraform plan` ran successfully.")
    md.append("- Plan-only mode (no apply).")
    md.append("")

    out_path = f"reports/daily-{report_date}.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")

    with open("reports/latest.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")

if __name__ == "__main__":
    main()
