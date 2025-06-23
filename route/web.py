from controller import HomeController

home_controller = HomeController()

def setupRoute(app):
    app.add_url_rule('/',             endpoint='home',         view_func=home_controller.index,        methods=['GET'])
    