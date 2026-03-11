import uuid
from decimal import Decimal

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import app
from app.models.composer import Composer, CopyrightStatus
from app.models.order import Order, OrderSource, PaymentStatus
from app.models.score import CopyrightType, Score, ScoreStatus
from app.models.task import Task, TaskPriority, TaskStatus, TaskType
from app.models.user import User, UserRole
from app.utils.security import create_access_token, hash_password

# Use SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionFactory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    async with TestSessionFactory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


# ==================== Factory Helpers ====================

async def create_test_user(
    session: AsyncSession,
    phone: str = "13800138000",
    email: str = "test@example.com",
    password: str = "testpass123",
    nickname: str = "TestUser",
    role: UserRole = UserRole.CUSTOMER,
) -> User:
    user = User(
        id=uuid.uuid4(),
        phone=phone,
        email=email,
        password_hash=hash_password(password),
        nickname=nickname,
        role=role,
    )
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user


async def create_test_admin(
    session: AsyncSession,
    phone: str = "13900139000",
    email: str = "admin@example.com",
) -> User:
    return await create_test_user(
        session, phone=phone, email=email, nickname="Admin", role=UserRole.ADMIN
    )


async def create_test_score(
    session: AsyncSession,
    title: str = "Für Elise",
    composer: str = "Beethoven",
    price: Decimal = Decimal("10.00"),
    status: ScoreStatus = ScoreStatus.AVAILABLE,
    copyright_status: CopyrightType = CopyrightType.PUBLIC_DOMAIN,
    pdf_url: str = "https://storage.example.com/scores/test.pdf",
) -> Score:
    score = Score(
        id=uuid.uuid4(),
        title=title,
        composer=composer,
        price=price,
        status=status,
        copyright_status=copyright_status,
        pdf_url=pdf_url,
        instrument="piano",
        difficulty=3,
    )
    session.add(score)
    await session.flush()
    await session.refresh(score)
    return score


async def create_test_order(
    session: AsyncSession,
    user: User,
    score: Score,
    amount: Decimal | None = None,
    payment_status: PaymentStatus = PaymentStatus.PENDING,
) -> Order:
    order = Order(
        id=uuid.uuid4(),
        user_id=user.id,
        score_id=score.id,
        amount=amount or score.price,
        source=OrderSource.WEBSITE,
        payment_status=payment_status,
    )
    session.add(order)
    await session.flush()
    await session.refresh(order)
    return order


async def create_test_task(
    session: AsyncSession,
    title: str = "Test Task",
    task_type: TaskType = TaskType.CUSTOMER_TRANSCRIBE,
    status: TaskStatus = TaskStatus.PENDING,
    priority: TaskPriority = TaskPriority.HIGH,
) -> Task:
    task = Task(
        id=uuid.uuid4(),
        type=task_type,
        title=title,
        status=status,
        priority=priority,
    )
    session.add(task)
    await session.flush()
    await session.refresh(task)
    return task


async def create_test_composer(
    session: AsyncSession,
    name_zh: str = "贝多芬",
    name_en: str = "Beethoven",
    death_year: int = 1827,
    copyright_status: CopyrightStatus = CopyrightStatus.PUBLIC_DOMAIN,
) -> Composer:
    composer = Composer(
        id=uuid.uuid4(),
        name_zh=name_zh,
        name_en=name_en,
        death_year=death_year,
        birth_year=1770,
        copyright_status=copyright_status,
    )
    session.add(composer)
    await session.flush()
    await session.refresh(composer)
    return composer


def auth_header(user: User) -> dict:
    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return {"Authorization": f"Bearer {token}"}
