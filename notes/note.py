from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from datetime import datetime, timezone

from notes.db import get_db

bp = Blueprint("note", __name__)


@bp.route("/")
def index():
    """Show all the notes, most recent first."""
    db = get_db()
    notes = db.execute(
        "SELECT id, body, created, modified"
        " FROM notes"
        " ORDER BY modified DESC"
    )
    if notes:
        notes = notes.fetchall()
    return render_template("note/index.html", notes=notes)


def get_note(id):
    """Get a note by id"""
    note = (
        get_db()
        .execute(
            "SELECT id, body, created, modified"
            " FROM notes p"
            " WHERE id = ?",
            (id,),
        )
        .fetchone()
    )

    if note is None:
        abort(404, f"Note id {id} doesn't exist.")

    return note


@bp.route("/create", methods=("GET", "POST"))
def create():
    if request.method == "POST":
        body = request.form["body"]
        error = None

        if not body:
            error = "Body is required."

        if error is not None:
            flash(error)

        else:
            db = get_db()

            modified_time = datetime.now(timezone.utc)

            db.execute(
                "INSERT INTO notes (body) VALUES (?)",
                (body,),
            )

            id_cursor = db.execute("SELECT LAST_INSERT_ROWID()")
            note_id = tuple(id_cursor.fetchall()[0])[0]
            print(note_id)

            db.execute(
                "INSERT INTO history (note_id, modified, body) VALUES (?, ?, ?)",
                (note_id, modified_time, body)
            )
            db.commit()
            return redirect(url_for("note.index"))

    return render_template("note/create.html")


@bp.route("/<int:id>/edit", methods=("GET", "POST"))
def edit(id):
    """Update a note."""
    note = get_note(id)

    if request.method == "POST":
        body = request.form["body"]
        error = None

        if error is not None:
            flash(error)
        else:
            db = get_db()

            modified_time = datetime.now(timezone.utc)

            db.execute(
                "UPDATE notes SET body = ?, modified = ? WHERE id = ?", (body, modified_time, note['id'])
            )

            db.execute(
                "INSERT INTO history (note_id, modified, body) VALUES (?, ?, ?)",
                (note['id'], modified_time, body)
            )
            db.commit()

            return redirect(url_for("note.index"))

    return render_template("note/edit.html", note=note)


@bp.route("/<int:id>/history", methods=("GET",))
def get_history(id):
    note = get_note(id)
    db = get_db()
    history = db.execute("SELECT * FROM history WHERE note_id = ? ORDER BY modified DESC", (note['id'],)).fetchall()
    return render_template("note/history.html", history=history)


@bp.route("/<int:id>/delete", methods=("POST",))
def delete(id):
    """Delete a note"""
    db = get_db()
    db.execute("DELETE FROM notes WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("note.index"))
