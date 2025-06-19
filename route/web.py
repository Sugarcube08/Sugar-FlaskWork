from controller import HomeController

def setupRoute(app):
    app.add_url_rule('/',             endpoint='home',         view_func=HomeController.index,        methods=['GET'])
    