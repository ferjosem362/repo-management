from flask import Flask
from flask_graphql import GraphQLView
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

# Database setup
Base = declarative_base()
engine = create_engine('sqlite:///github_data.db')
db_session = scoped_session(sessionmaker(bind=engine))

class Repo(Base):
    __tablename__ = 'repos'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    commit_date = Column(String)
    committer = Column(String)
    admin_access = Column(Boolean)
    creation_date = Column(String)
    creator = Column(String)
    archived = Column(Boolean)
    size = Column(Integer)

class RepoObject(SQLAlchemyObjectType):
    class Meta:
        model = Repo
        interfaces = (graphene.relay.Node, )

class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    all_repos = SQLAlchemyConnectionField(RepoObject)

app = Flask(__name__)
app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=graphene.Schema(query=Query, types=[RepoObject]), graphiql=True))

if __name__ == '__main__':
    app.run()
