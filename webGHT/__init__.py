import os
import configparser

from flask import Flask

from . import setting

def create_app(test_config=None):
    # get db path
    config = configparser.ConfigParser()
    config.read(os.path.abspath(os.path.join(".ini")))
    
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='123',
        # DATABASE=os.path.join(app.instance_path, 'webGHT.sqlite')
    )
    app.config['DEBUG'] = True
    app.config['MONGO_URI'] = config['PROD']['DB_URI']

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that used to checking
    @app.route('/ping')
    def hello():
        return 'Healthy!'
    
    # init db
    from . import db
    db.init_app(app)

    # import and register blueprint 
    from . import auth, tool
    app.register_blueprint(auth.bp)
    app.register_blueprint(tool.bp)
    app.register_blueprint(setting.bp)
    
    app.add_url_rule('/', endpoint='index')
        
    return app