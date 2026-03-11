import uuid

from tests.conftest import auth_header, create_test_admin, create_test_task, create_test_user
from app.models.task import TaskStatus, TaskType


class TestTasksAPI:
    """Tasks API tests: normal, boundary, exception cases."""

    # --- Normal cases ---
    async def test_create_task(self, client, db_session):
        admin = await create_test_admin(db_session)
        resp = await client.post(
            "/api/v1/tasks",
            json={
                "type": "customer_transcribe",
                "title": "月光奏鸣曲",
            },
            headers=auth_header(admin),
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["type"] == "customer_transcribe"
        assert data["priority"] == "high"

    async def test_list_tasks(self, client, db_session):
        admin = await create_test_admin(db_session)
        await create_test_task(db_session, title="T1")
        resp = await client.get(
            "/api/v1/tasks",
            headers=auth_header(admin),
        )
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

    async def test_get_task(self, client, db_session):
        admin = await create_test_admin(db_session)
        task = await create_test_task(db_session)
        resp = await client.get(
            f"/api/v1/tasks/{task.id}",
            headers=auth_header(admin),
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == task.title

    async def test_approve_task(self, client, db_session):
        admin = await create_test_admin(db_session)
        task = await create_test_task(db_session, status=TaskStatus.REVIEW)
        resp = await client.post(
            f"/api/v1/tasks/{task.id}/approve",
            json={"admin_notes": "LGTM"},
            headers=auth_header(admin),
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "approved"

    async def test_discard_task(self, client, db_session):
        admin = await create_test_admin(db_session)
        task = await create_test_task(db_session, status=TaskStatus.PENDING)
        resp = await client.post(
            f"/api/v1/tasks/{task.id}/discard",
            headers=auth_header(admin),
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "discarded"

    async def test_list_by_type(self, client, db_session):
        admin = await create_test_admin(db_session)
        await create_test_task(db_session, task_type=TaskType.PROACTIVE_IMPORT)
        resp = await client.get(
            "/api/v1/tasks?task_type=proactive_import",
            headers=auth_header(admin),
        )
        assert resp.status_code == 200

    # --- Boundary cases ---
    async def test_list_empty(self, client, db_session):
        admin = await create_test_admin(db_session)
        resp = await client.get("/api/v1/tasks", headers=auth_header(admin))
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    # --- Exception cases ---
    async def test_customer_cannot_access(self, client, db_session):
        user = await create_test_user(db_session)
        resp = await client.get("/api/v1/tasks", headers=auth_header(user))
        assert resp.status_code == 403

    async def test_no_auth(self, client):
        resp = await client.get("/api/v1/tasks")
        assert resp.status_code == 401

    async def test_get_nonexistent(self, client, db_session):
        admin = await create_test_admin(db_session)
        resp = await client.get(
            f"/api/v1/tasks/{uuid.uuid4()}",
            headers=auth_header(admin),
        )
        assert resp.status_code == 404

    async def test_approve_pending_task_fails(self, client, db_session):
        admin = await create_test_admin(db_session)
        task = await create_test_task(db_session, status=TaskStatus.PENDING)
        resp = await client.post(
            f"/api/v1/tasks/{task.id}/approve",
            json={},
            headers=auth_header(admin),
        )
        assert resp.status_code == 400

    async def test_discard_delivered_fails(self, client, db_session):
        admin = await create_test_admin(db_session)
        task = await create_test_task(db_session, status=TaskStatus.DELIVERED)
        resp = await client.post(
            f"/api/v1/tasks/{task.id}/discard",
            headers=auth_header(admin),
        )
        assert resp.status_code == 400
