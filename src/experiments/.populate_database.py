from data_scraping.crawler import Crawler
from sqlalchemy.orm import backref, relation, sessionmaker, relationship
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float
import os
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
db_password = os.environ["POSTGRES_PASSWORD"]
engine = create_engine(f"postgresql+psycopg2://moritz:{db_password}@localhost/edgar")
Session = sessionmaker(bind=engine)
session = Session()


spider = Crawler("0001318605")
spider.populate_facts()


class Period(Base):
    __tablename__ = "periods"

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    period = Column(String, unique=True)

    # relationships
    facts_rel = relationship("Fact", back_populates="period_rel")


class Fact(Base):
    __tablename__ = "facts"

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    company_name = Column(String)
    name = Column(String)
    period = Column(String, ForeignKey("periods.period"))
    value = Column(Float)
    unit = Column(String)

    # realtionships
    period_rel = relationship("Period", back_populates="facts_rel")

    def __repr__(self) -> str:
        return f"[{self.company_name}] {self.name} {self.period} = {self.value} {self.unit}"


Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


class CrawlerToDatabaseAdapter:
    def __init__(self, crawler: Crawler, session):
        self.crawler = crawler
        self.session = session

        # load exising periods
        self.period_objs = dict()
        for x in self.session.query(Period).all():
            self.period_objs[x.period] = x

        # load existing fact ids
        self.existing_facts = set()
        for x in self.session.query(Fact).all():
            self.existing_facts.add(f"{x.company_name}_{x.name}_{x.period}")

    def populate_database(self):
        facts = []
        for fact_name in self.crawler.facts:
            unit = list(self.crawler.facts[fact_name]["units"].keys())[0]
            for period in self.crawler.facts[fact_name]["units"][unit]:

                # if fact exists, do not re-create it
                if (
                    f"{self.crawler.company_name}_{fact_name}_{period}"
                    in self.existing_facts
                ):
                    continue

                # period either exists or needs to be created
                period_name = f"{period['fp']}{period['fy']}"

                if period_name not in self.period_objs:
                    period_obj = Period(period=period_name)
                    self.period_objs[period_name] = period_obj
                else:
                    period_obj = self.period_objs[period_name]

                # create fact
                fact = Fact(
                    company_name=self.crawler.company_name,
                    name=fact_name,
                    period_rel=period_obj,
                    value=period["val"],
                    unit=unit,  # actual unit, e.g. USD
                )

                facts.append(fact)

                # update existing facts
                self.existing_facts.add(
                    f"{self.crawler.company_name}_{fact_name}_{period}"
                )

        session.add_all(facts)
        self.session.commit()


adapter = CrawlerToDatabaseAdapter(spider, session)
adapter.populate_database()

for x in session.query(Fact):
    print(x)

print("done")
