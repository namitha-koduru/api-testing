from flask import Blueprint

from service.taskservice import (
    add_task_service,
    get_task_service,
    update_task_service,
    patch_task_service,
    delete_task_service
)

task_bp = Blueprint(
    'task_bp',
    __name__
)

@task_bp.route('/tasks', methods=['POST'])
def add_task():
    return add_task_service()


@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    return get_task_service()


@task_bp.route('/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    return update_task_service(id)


@task_bp.route('/tasks/<int:id>/status', methods=['PATCH'])
def patch_status(id):
    return patch_task_service(id)


@task_bp.route('/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    return delete_task_service(id)