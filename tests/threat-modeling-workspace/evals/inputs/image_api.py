"""Image API — Flask handlers for the image processing service."""

import os
import json
import uuid
import jwt
import pika
import boto3
from flask import Flask, request, jsonify, redirect

app = Flask(__name__)

DB_CONN = os.environ.get("DATABASE_URL")
S3_BUCKET = os.environ.get("S3_BUCKET", "image-uploads")
RABBITMQ_URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")

s3 = boto3.client("s3")


# ---------- helpers ----------

def get_current_user():
    """Decode JWT from Authorization header."""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    # NOTE: algorithm not pinned; audience not checked
    payload = jwt.decode(token, options={"verify_signature": True})
    return payload


def is_operator(user):
    return user.get("role") == "operator"


def publish_transform_job(image_id, operations, callback_url):
    conn = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    ch = conn.channel()
    ch.queue_declare(queue="image-transforms")
    ch.basic_publish(
        exchange="",
        routing_key="image-transforms",
        body=json.dumps({
            "image_id": image_id,
            "operations": operations,
            "callback_url": callback_url,
        }),
    )
    conn.close()


# ---------- public endpoints ----------

@app.route("/images", methods=["POST"])
def upload_image():
    user = get_current_user()
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "No file provided"}), 400

    image_id = str(uuid.uuid4())
    # Upload directly — no size limit, no MIME validation
    s3.upload_fileobj(f, S3_BUCKET, f"uploads/{image_id}/{f.filename}")

    # Store metadata — owner comes from JWT, but filename from client
    import psycopg2
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO images (id, owner_id, filename, mime_type) VALUES (%s, %s, %s, %s)",
        (image_id, user["sub"], f.filename, f.content_type),
    )
    conn.commit()
    conn.close()
    print(f"Uploaded image {image_id} for user {user['sub']}")
    return jsonify({"id": image_id}), 201


@app.route("/images/<image_id>", methods=["GET"])
def get_image(image_id):
    user = get_current_user()
    import psycopg2
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("SELECT id, owner_id, filename FROM images WHERE id = %s", (image_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Not found"}), 404
    # No ownership check — any authenticated user can view any image metadata
    return jsonify({"id": row[0], "owner_id": row[1], "filename": row[2]})


@app.route("/images/<image_id>/download", methods=["GET"])
def download_image(image_id):
    user = get_current_user()
    import psycopg2
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("SELECT owner_id, filename FROM images WHERE id = %s", (image_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Not found"}), 404
    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": S3_BUCKET, "Key": f"uploads/{image_id}/{row[1]}"},
        ExpiresIn=3600,
    )
    return redirect(url)


@app.route("/images/<image_id>", methods=["DELETE"])
def delete_image(image_id):
    user = get_current_user()
    # Soft-delete — but no ownership check
    import psycopg2
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("UPDATE images SET deleted = TRUE WHERE id = %s", (image_id,))
    conn.commit()
    conn.close()
    return "", 204


@app.route("/images/<image_id>/transform", methods=["POST"])
def request_transform(image_id):
    user = get_current_user()
    body = request.get_json()
    # callback_url comes from user input — SSRF risk
    publish_transform_job(image_id, body.get("operations", []), body["callback_url"])
    return jsonify({"status": "queued"}), 202


# ---------- admin endpoints ----------

@app.route("/admin/images", methods=["GET"])
def admin_list_images():
    user = get_current_user()
    if not is_operator(user):
        return jsonify({"error": "Forbidden"}), 403
    import psycopg2
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    # No pagination — returns all rows
    cur.execute("SELECT id, owner_id, filename FROM images WHERE deleted = FALSE")
    rows = cur.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "owner_id": r[1], "filename": r[2]} for r in rows])


@app.route("/admin/images/<image_id>/moderate", methods=["POST"])
def admin_moderate(image_id):
    user = get_current_user()
    if not is_operator(user):
        return jsonify({"error": "Forbidden"}), 403
    action = request.json.get("action")  # "flag" or "remove"
    import psycopg2
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    if action == "remove":
        cur.execute("UPDATE images SET deleted = TRUE WHERE id = %s", (image_id,))
    cur.execute(
        "INSERT INTO moderation_log (operator_id, image_id, action) VALUES (%s, %s, %s)",
        (user["sub"], image_id, action),
    )
    conn.commit()
    conn.close()
    print(f"Moderation: {user['sub']} performed {action} on {image_id}")
    return jsonify({"status": "ok"})
