import os

from flask import Flask, send_file, render_template, request
from flask_restful import Api, Resource
from . import db
from . import logger

app = Flask(__name__)
api = Api(app)

app.config.from_mapping(
    DATABASE=os.path.join(app.instance_path, 'tourdeflask.sqlite'),
)

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

db.init_app(app)
logger.init()

@app.route('/')
def hello_world():  # put application's code here
    return render_template("index.html")

@app.route("/snake")
def snake():
    return render_template("lol.html")

@app.route("/lecturer/<uuid>")
def lecturer_view(uuid):
    lecturer = db.get_lecturer(uuid)
    print(lecturer)
    return render_template("lecturer.html", lecturer = lecturer[0])

# API
@app.route("/api")
def api_tester():
    return render_template("api_tester.html")


@app.route("/log")
def log():
    return logger.get()


class Lecturers(Resource):
    def post(self):
        data_json = request.get_json()
        logger.log(f"---------------------------------<br>{request.url}")
        logger.log(f"{request.args}")
        logger.log(f"{str(request.get_json())}<br>---------------------------------")
        return db.create_new_lecturer(data_json)

    def get(self):
        logger.log(f"---------------------------------<br>{request.url}<br>---------------------------------")
        logger.log("ete?")
        return db.get_lecturers()

    def delete(self):
        db.drop_tables()
        db.setup_tables()
        return {}, 204


class Lecturer(Resource):
    def get(self, uuid):
        logger.log(f"---------------------------------<br>{request.url}<br>---------------------------------")
        return db.get_lecturer(uuid)

    def put(self, uuid):
        data = request.get_json()
        print(data)
        logger.log(f"---------------------------------<br>{request.url}")
        logger.log(f"{request.args}")
        logger.log(f"{str(data)}<br>---------------------------------")
        return db.update_lecturer(uuid, data)

    def delete(self, uuid):
        logger.log(f"---------------------------------<br>{request.url}<br>---------------------------------")
        return db.delete_lecturer(uuid)


class SearchUtils(Resource):
    def get(self):
        data = {
            "locations": db.get_all_locations(),
            "tags": db.get_all_tags(),
            "price_range": db.get_price_range()
        }



        return data

class Search(Resource):
    def post(self):
        data = request.get_json()

        for key in ['location', 'tags', 'pay_min', 'pay_max']:
            if key not in data:
                data[key] = None


        lecturer_shuffle = db.get_search_lecturers_shuffle(data['location'], data['tags'], data['pay_min'], data['pay_max'])

        page_0 = lecturer_shuffle[0:min(len(lecturer_shuffle), 100)]

        lecturers_page_0 = db.search_lecturers(page_0)

        return {'search' : lecturers_page_0, 'shuffle' : lecturer_shuffle}, 200


class SearchPage(Resource):
    def post(self):
        data = request.get_json()

        if 'rowids' not in data:
            return {}, 400


        search = db.search_lecturers(data['rowids'])

        return search, 200



api.add_resource(Lecturers, "/api/lecturers")
api.add_resource(Lecturer, "/api/lecturers/<uuid>")
api.add_resource(SearchUtils, "/api/searchutils")
api.add_resource(Search, "/api/search")
api.add_resource(SearchPage, "/api/getpage")


if __name__ == '__main__':
    app.run(debug = True)
