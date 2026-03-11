import uuid
from decimal import Decimal

from tests.conftest import auth_header, create_test_admin, create_test_score, create_test_user


class TestScoresAPI:
    """Scores API tests: normal, boundary, exception cases."""

    # --- Normal cases ---
    async def test_list_scores(self, client, db_session):
        await create_test_score(db_session, title="Score 1")
        await create_test_score(db_session, title="Score 2", price=Decimal("20.00"))
        resp = await client.get("/api/v1/scores")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    async def test_get_score(self, client, db_session):
        score = await create_test_score(db_session)
        resp = await client.get(f"/api/v1/scores/{score.id}")
        assert resp.status_code == 200
        assert resp.json()["title"] == "Für Elise"

    async def test_create_score_as_admin(self, client, db_session):
        admin = await create_test_admin(db_session)
        resp = await client.post(
            "/api/v1/scores",
            json={"title": "New Score", "price": "15.00"},
            headers=auth_header(admin),
        )
        assert resp.status_code == 201
        assert resp.json()["title"] == "New Score"

    async def test_update_score_as_admin(self, client, db_session):
        admin = await create_test_admin(db_session)
        score = await create_test_score(db_session)
        resp = await client.put(
            f"/api/v1/scores/{score.id}",
            json={"title": "Updated"},
            headers=auth_header(admin),
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "Updated"

    async def test_delete_score_as_admin(self, client, db_session):
        admin = await create_test_admin(db_session)
        score = await create_test_score(db_session)
        resp = await client.delete(
            f"/api/v1/scores/{score.id}",
            headers=auth_header(admin),
        )
        assert resp.status_code == 204

    # --- Filter by instrument ---
    async def test_list_by_instrument(self, client, db_session):
        await create_test_score(db_session)  # piano
        resp = await client.get("/api/v1/scores?instrument=piano")
        assert resp.status_code == 200

    # --- Filter by price range ---
    async def test_list_by_price_range(self, client, db_session):
        await create_test_score(db_session, title="Cheap", price=Decimal("5.00"))
        resp = await client.get("/api/v1/scores?min_price=1&max_price=10")
        assert resp.status_code == 200

    # --- Boundary cases ---
    async def test_list_scores_empty(self, client):
        resp = await client.get("/api/v1/scores")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    async def test_list_scores_pagination(self, client, db_session):
        for i in range(5):
            await create_test_score(db_session, title=f"S{i}", price=Decimal(str(i + 1)))
        resp = await client.get("/api/v1/scores?page=1&page_size=2")
        assert resp.status_code == 200
        assert len(resp.json()["items"]) == 2

    # --- Exception cases ---
    async def test_get_nonexistent_score(self, client):
        resp = await client.get(f"/api/v1/scores/{uuid.uuid4()}")
        assert resp.status_code == 404

    async def test_create_score_as_customer(self, client, db_session):
        user = await create_test_user(db_session)
        resp = await client.post(
            "/api/v1/scores",
            json={"title": "Forbidden"},
            headers=auth_header(user),
        )
        assert resp.status_code == 403

    async def test_create_score_no_auth(self, client):
        resp = await client.post("/api/v1/scores", json={"title": "No Auth"})
        assert resp.status_code == 401

    async def test_delete_nonexistent(self, client, db_session):
        admin = await create_test_admin(db_session)
        resp = await client.delete(
            f"/api/v1/scores/{uuid.uuid4()}",
            headers=auth_header(admin),
        )
        assert resp.status_code == 404

    async def test_create_score_missing_title(self, client, db_session):
        admin = await create_test_admin(db_session)
        resp = await client.post(
            "/api/v1/scores",
            json={"price": "10.00"},
            headers=auth_header(admin),
        )
        assert resp.status_code == 422

    async def test_create_score_invalid_difficulty(self, client, db_session):
        admin = await create_test_admin(db_session)
        resp = await client.post(
            "/api/v1/scores",
            json={"title": "Test", "difficulty": 10},
            headers=auth_header(admin),
        )
        assert resp.status_code == 422
