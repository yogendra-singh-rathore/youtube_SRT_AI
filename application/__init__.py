import os
from flask import Flask
from application.utils.path_handler import paths
from application.config.db_conn import get_db_connection
from application.config.database import database_execution

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.urandom(24)

#initiazlize the database
get_db_connection()
database_execution()
paths()

# Set the ImageMagick path
if os.name == 'nt':  # Windows
    os.environ['IMAGEMAGICK_BINARY'] = r"C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"  # Update with your ImageMagick path
else:
    os.environ['IMAGEMAGICK_BINARY'] = "/opt/homebrew/bin/convert"  # Update if necessary for Linux/Mac


#Blue Prints
from application.routes.core import core
from application.routes.srt import srt
from application.routes.upload import upload
from application.routes.youtube import yt

app.register_blueprint(core)
app.register_blueprint(srt)
app.register_blueprint(upload)
app.register_blueprint(yt)