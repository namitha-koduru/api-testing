from flask import request, jsonify

from model.taskmodel import Task
from config.db import db


def add_task_service():

    data = request.json

    task = Task(
        title=data['title'],
        description=data['description']
    )

    db.session.add(task)
    db.session.commit()

    return jsonify({
        "message": "Task added successfully"
    }), 201


def get_task_service():

    tasks = Task.query.all()

    result = []

    for task in tasks:

        result.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status
        })

    return jsonify(result)


def update_task_service(id):

    task = Task.query.get(id)

    if not task:
        return jsonify({
            "message": "Task not found"
        }), 404

    data = request.json

    task.title = data['title']
    task.description = data['description']

    db.session.commit()

    return jsonify({
        "message": "Task updated"
    })


def patch_task_service(id):

    task = Task.query.get(id)

    if not task:
        return jsonify({
            "message": "Task not found"
        }), 404

    data = request.json

    task.status = data['status']

    db.session.commit()

    return jsonify({
        "message": "Status updated"
    })


def delete_task_service(id):

    task = Task.query.get(id)

    if not task:
        return jsonify({
            "message": "Task not found"
        }), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({
        "message": "Task deleted"
    })