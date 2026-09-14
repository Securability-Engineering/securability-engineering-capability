"""Async data export handler."""

import csv
import io

import boto3
from flask import Blueprint, request, jsonify, g
from celery import shared_task
from models import db, Customer

exports_bp = Blueprint("exports", __name__)

S3_BUCKET = "company-exports"
s3 = boto3.client("s3")


@shared_task
def run_export(export_name: str, user_id: str):
    """Export all customer records to S3 as CSV."""
    customers = Customer.query.all()

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "email", "phone", "billing_address", "plan"])
    for c in customers:
        writer.writerow([c.id, c.email, c.phone, c.billing_address, c.plan])

    key = f"exports/{export_name}.csv"
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=buf.getvalue(),
        ACL="public-read",
    )
    print(f"Export complete: s3://{S3_BUCKET}/{key}")
    return key


@exports_bp.route("/api/exports", methods=["POST"])
def create_export():
    data = request.get_json(force=True)
    export_name = data.get("export_name", f"export-{g.user_id}")

    task = run_export.delay(export_name, g.user_id)
    return jsonify({"task_id": task.id, "status": "queued"}), 202
