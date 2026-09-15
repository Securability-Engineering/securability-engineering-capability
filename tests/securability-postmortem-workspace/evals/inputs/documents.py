"""Document storage API handlers."""

from flask import Blueprint, request, jsonify, g
from models import db, Document

documents_bp = Blueprint("documents", __name__)


@documents_bp.before_request
def load_user():
    """Populate g.user from the session middleware."""
    # Session middleware sets g.user_id from a signed cookie
    g.user_id = request.headers.get("X-User-Id")  # simplified for demo


@documents_bp.route("/api/documents", methods=["POST"])
def create_document():
    """Create a new document owned by the current user."""
    data = request.get_json(force=True)
    doc = Document(
        title=data.get("title", "Untitled"),
        content=data.get("content", ""),
        owner_id=g.user_id,
    )
    db.session.add(doc)
    db.session.commit()
    print(f"Document created: {doc.id}")
    return jsonify({"id": doc.id, "title": doc.title}), 201


@documents_bp.route("/api/documents/<int:doc_id>", methods=["GET"])
def get_document(doc_id: int):
    """Return a single document by ID."""
    doc = Document.query.get(doc_id)
    if doc is None:
        return jsonify({"error": "not found"}), 404
    return jsonify({
        "id": doc.id,
        "title": doc.title,
        "content": doc.content,
        "metadata": doc.metadata,
        "owner_id": doc.owner_id,
    })


@documents_bp.route("/api/documents/<int:doc_id>", methods=["DELETE"])
def delete_document(doc_id: int):
    doc = Document.query.get(doc_id)
    if doc is None:
        return jsonify({"error": "not found"}), 404
    db.session.delete(doc)
    db.session.commit()
    return "", 204
