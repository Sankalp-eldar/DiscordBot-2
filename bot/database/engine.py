from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from ..constants import ENGINE

engine = create_async_engine(ENGINE, future=True, hide_parameters=True)

Session = sessionmaker( engine, expire_on_commit=False, class_= AsyncSession, future= True )



async def main():
    from sqlalchemy import text
    async with Session() as session:
        res = (await session.execute(text("Show tables"))).scalar()
        print(res)

if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
