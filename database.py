
# system imports
import os

# Stock Database specific
from sqlalchemy import create_engine, desc, asc
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

Base = automap_base()
# using environment variables for now..
engine = create_engine("%s://%s:%s@%s/%s" % (os.environ['swtype'],
                                             os.environ['swuser'],
                                             os.environ['swpassword'],
                                             os.environ['swhost'],
                                             os.environ['swdatabase'])
                       )
Base.prepare(engine, reflect=True)
Company = Base.classes.company
Indicators = Base.classes.indicators
session = Session(engine)
