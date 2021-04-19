''' BEGIN CONFIG '''
from etc.config.externalLib import *

from models.APP import forms, users, apis
from models.FHE import FHE_Client, FHE_Integer


app = Flask(__name__,
            template_folder='template',
            static_folder='static'
)

app.config.update(
    TEMPLATES_AUTO_RELOAD=True,
    SECRET_KEY='CISC499-FHE-Client-Key'
)


Misaka(app, fenced_code=True)


from views.about import *
from views.database_connect import *
from views.database_login import *
from views.database_session import *
from views.usage import *
