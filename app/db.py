import json
import random

import click
from flask import current_app, g
from flask.cli import with_appcontext
from uuid import uuid4
from . import logger

import sqlite3




LECTURER_TABLE_VALUES = ["title_before", "first_name", "middle_name", "last_name", "title_after", "picture_url", "location", "claim", "bio", "price_per_hour", "contact"]
LECTURER_TABLE_VALUES_MANDATORY = ["first_name", "last_name"]


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES,
            check_same_thread=False
        )
        #g.db.row_factory = sqlite3.Row

    return g.db


def get_db_cur():
    if 'db_cur' not in g:
        g.db_cur = get_db().cursor()

    return g.db_cur


def close_db_cur(e = None):
    db_cur = g.pop('db_cur', None)

    if db_cur is not None:
        db_cur.close()

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    """
    Inicializuje databázi dle schema.sql
    """
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

    #drop_tables()
    setup_tables()


def drop_tables():
    get_db_cur().execute("""DROP TABLE IF EXISTS lecturers""")
    get_db_cur().execute("""DROP TABLE IF EXISTS lecturers_tags""")
    get_db_cur().execute("""DROP TABLE IF EXISTS tags""")
    get_db().commit()

def setup_tables():
    get_db_cur().execute("""CREATE TABLE IF NOT EXISTS lecturers(
        uuid TEXT,
        title_before VARCHAR(255),
        first_name VARCHAR(255) NOT NULL,
        middle_name VARCHAR(255),
        last_name VARCHAR(255) NOT NULL,
        title_after VARCHAR(255),
        picture_url TEXT,
        location VARCHAR(255),
        claim TEXT,
        bio TEXT,
        price_per_hour INT,
        contact TEXT,
        PRIMARY KEY(uuid)
    )""")

    get_db_cur().execute("""CREATE TABLE IF NOT EXISTS tags(
        uuid TEXT,
        name TEXT NOT NULL,
        PRIMARY KEY(uuid)
    )""")

    get_db_cur().execute("""CREATE TABLE IF NOT EXISTS lecturers_tags(
        lecturer_rowid INT,
        tag_rowid INT
    )""")


    get_db_cur().execute("""SELECT * FROM lecturers""")
    get_db().commit()


def create_new_lecturer(data):
    # generate new uuid for new lecturer
    data['uuid'] = str(uuid4())

    if 'contact' not in data:
        return {'code': 400, 'message' : 'bad request'}, 400
    data['contact'] = json.dumps(data['contact'])

    # check if we have all the data required
    data_tuple = []
    for key in LECTURER_TABLE_VALUES:
        if key not in data:
            if key in LECTURER_TABLE_VALUES_MANDATORY: return {'code': 400, "message": f"missing {key}"}, 400
            data[key] = None
        elif data[key] is None and key in LECTURER_TABLE_VALUES_MANDATORY: return {'code': 400, "message": f"missing {key}"}, 400
        data_tuple.append(data[key])
    data_tuple.insert(0, data['uuid'])

    # insert into table
    get_db_cur().execute("""INSERT INTO lecturers(
        uuid, title_before, first_name, middle_name,
        last_name, title_after, picture_url, location,
        claim, bio, price_per_hour, contact
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", data_tuple)

    # get lecturer id
    lecturer_id = lecturer_uuid_2_id(data['uuid'])


    data['tags'] = add_tags_to_lecturer(data['tags'], lecturer_id)
    data['contact'] = json.loads(data['contact'])
    get_db().commit()
    return data, 200



def add_tags_to_lecturer(tags, lecturer_id):
    # add all lecturer tags
    for tag_i in range(len(tags)):
        if 'uuid' not in tags[tag_i]:
            # if no uuid provided try to find this tag in the DB using name
            get_db_cur().execute("""SELECT uuid FROM tags WHERE name = ?""", (tags[tag_i]['name'],))
            tag_rows = get_db_cur().fetchall()

            # if the tag new -> create new uuid
            if len(tag_rows) == 0:
                tags[tag_i]['uuid'] = str(uuid4())
            else: # else use uuid from db
                tags[tag_i]['uuid'] = tag_rows[0][0]
        add_tag_to_lecturer(tags[tag_i]['uuid'], lecturer_id, tags[tag_i]['name'])
    return tags

def add_tag_to_lecturer(tag_uuid, lecturer_id, name_if_no_uuid = ""):
    # search for tag id using UUID
    get_db_cur().execute("""SELECT rowid FROM tags WHERE uuid = ?""", (tag_uuid,))
    tags = get_db_cur().fetchall()

    # if nothing found -> create the tag -> get id
    if len(tags) == 0:
        create_new_tag(tag_uuid, name_if_no_uuid)
        get_db_cur().execute("""SELECT rowid FROM tags WHERE uuid = ?""", (tag_uuid,))
        tag_id = get_db_cur().fetchone()[0]
    else: # else get id
        tag_id = tags[0][0]

    # add tag to lecturer
    get_db_cur().execute("""INSERT INTO lecturers_tags(lecturer_rowid, tag_rowid) VALUES (?, ?)""", (lecturer_id, tag_id))
    get_db().commit()


def remove_lecturer_tags(lecturer_id):
    get_db_cur().execute("""DELETE FROM lecturers_tags WHERE lecturer_rowid = ?""", (lecturer_id,))

def create_new_tag(uuid, name):
    get_db_cur().execute("""INSERT INTO tags(uuid, name) VALUES (?, ?)""", (uuid, name))
    get_db().commit()

def get_lecturers_tags(lecturer_id):
    get_db_cur().execute("""
    SELECT uuid, name FROM lecturers_tags
    JOIN tags
    ON lecturers_tags.lecturer_rowid = ? and
    tags.rowid = lecturers_tags.tag_rowid
    """, (lecturer_id,))

    return get_db_cur().fetchall()

def get_lecturer(uuid):
    # get lecturer id
    get_db_cur().execute("""SELECT *, rowid FROM lecturers WHERE uuid= ?""", (uuid,))

    rows = get_db_cur().fetchall()

    if len(rows) == 0:
        return {"code": 404,"message": "User not found"}, 404

    return lecturer_data_from_row(rows[0]), 200

def get_lecturers():
    logger.log("GETTING")
    # gets ALL table data
    get_db_cur().execute("""SELECT *, rowid FROM lecturers""")
    row_data = get_db_cur().fetchall()
    lecturers = []
    logger.log("......")
    logger.log(str(row_data))
    # parses each row to desired format
    for row in row_data:
        lecturers.append(lecturer_data_from_row(row))
    print(lecturers)
    logger.log("..jaoidjaoidjaodj....")
    logger.log(str(lecturers))
    logger.log("......")
    return lecturers, 200


def update_lecturer(uuid, new_data):
    # get lecturer id
    lecturer_id = lecturer_uuid_2_id(uuid)

    if lecturer_id is None:
        return {"code": 404,"message": "User not found"}, 404

    if 'tags' in new_data:
        remove_lecturer_tags(lecturer_id)

        new_data['tags'] = add_tags_to_lecturer(new_data['tags'], lecturer_id)

    # parse contacts
    if 'contact' in new_data:
        new_data['contact'] = json.dumps(new_data['contact'])

    # add all changed values to be ? into mega query
    value_pairs = ()
    qmarks = ""

    for key in new_data.keys():
        if key in LECTURER_TABLE_VALUES:
            qmarks += f"{key} = ?, "
            #value_pairs += (key,)
            value_pairs += (new_data[key],)


    # add lecturer_id for search
    value_pairs += (lecturer_id,)

    print(value_pairs)
    print(qmarks)

    if qmarks != "":
        qmarks = qmarks[:-2]

        get_db_cur().execute(f"""
        UPDATE lecturers
        SET {qmarks}
        WHERE rowid = ?""", value_pairs)

        get_db().commit()

    return get_lecturer(uuid)


def delete_lecturer(uuid):
    # get lecturer id
    lecturer_id = lecturer_uuid_2_id(uuid)

    if lecturer_id is None:
        return {"code": 404,"message": "User not found"}, 404

    remove_lecturer_tags(lecturer_id)

    get_db_cur().execute("""DELETE FROM lecturers WHERE rowid = ?""", (lecturer_id,))
    get_db().commit()

    return {"code": 204, "message": "úspěšně smazán"}, 204


def lecturer_uuid_2_id(uuid):
    # get lecturer id
    get_db_cur().execute("""SELECT rowid FROM lecturers WHERE uuid = ?""", (uuid,))
    lecturer_id = get_db_cur().fetchall()

    if len(lecturer_id) == 0:
        return None

    return lecturer_id[0][0]


def lecturer_data_from_row(row):
    # uuid
    lecturer_data = {'uuid': row[0]}

    # table values
    for i in range(len(LECTURER_TABLE_VALUES)):
        lecturer_data[LECTURER_TABLE_VALUES[i]] = row[i + 1]

    # parse contact json
    lecturer_data['contact'] = json.loads(lecturer_data['contact'])

    # tags
    lecturer_data['tags'] = []
    for tag in get_lecturers_tags(row[-1]):
        lecturer_data['tags'].append({"uuid" : tag[0], "name" : tag[1]})

    return lecturer_data

def get_all_locations():
    get_db_cur().execute("""SELECT DISTINCT location FROM lecturers""")
    locations_raw = get_db_cur().fetchall()

    locations = []
    for location in locations_raw:
        locations.append(location[0])

    return locations


def get_price_range():
    get_db_cur().execute("""SELECT MAX(price_per_hour), MIN(price_per_hour) FROM lecturers""")
    price_rows = get_db_cur().fetchone()
    return [price_rows[1], price_rows[0]]

def get_all_tags():
    get_db_cur().execute("""SELECT * FROM tags""")
    tags_raw = get_db_cur().fetchall()

    tags = []
    for tag in tags_raw:
        tags.append({"uuid": tag[0], "name": tag[1]})

    return tags


def search_lecturers(row_ids=None):
    if row_ids is None:
        row_ids = []
    mega_query = f"""
    SELECT uuid, title_before, first_name, middle_name, last_name, title_after, picture_url, location, claim, bio, price_per_hour, contact, lecturers.ROWID as l_rid FROM lecturers
    WHERE ROWID in ({("?," * len(row_ids))[:-1]})
    """

    get_db_cur().execute(mega_query, row_ids)
    lecturer_rows = get_db_cur().fetchall()

    lectures = []


    sorted_ids = sorted(row_ids)

    for i in range(len(row_ids)):
        lectures.append(lecturer_data_from_row(lecturer_rows[sorted_ids.index(row_ids[i])]))

    return lectures


def get_search_lecturers_shuffle(location, tags, pay_min, pay_max):
    where = ""
    params = []

    if location is not None:
        params.append(location)
        where += " location = ? and"

    if pay_min is not None:
        params.append(pay_min)
        where += " price_per_hour >= ? and"

    if pay_max is not None:
        params.append(pay_max)
        where += " price_per_hour <= ? and"


    if tags is not None:
        if where != "":
            where = " and" + where[:-3]

        for tag in tags:
            params.append(tag)

        params.append(len(tags))

        # query thats mega
        mega_query = f"""
        SELECT DISTINCT lecturers.ROWID as l_rid FROM lecturers_tags
        JOIN lecturers
        ON lecturer_rowid = lecturers.rowid{where}
        /*JOIN tags
        ON tags.rowid = tag_rowid*/ and
        (SELECT COUNT(*) FROM lecturers_tags
            JOIN tags
            ON lecturers_tags.lecturer_rowid = l_rid and
            lecturers_tags.tag_rowid = tags.ROWID
            and tags.uuid in ({("?," * len(tags))[:-1]})
        ) = ?
        
        """
        print(mega_query)
        get_db_cur().execute(mega_query, params)
        lecturer_rows = get_db_cur().fetchall()
    else:
        if where != "": where = f"WHERE{where[:-3]}"
        get_db_cur().execute(f"SELECT rowid FROM lecturers {where}", params)
        lecturer_rows = get_db_cur().fetchall()

    lecturer_rids = []
    print(lecturer_rows)
    for row in lecturer_rows:
        lecturer_rids.append(row[0])

    random.shuffle(lecturer_rids)

    return lecturer_rids




@click.command('init-db')
@with_appcontext
def init_db_command():
    """
    Definujeme příkaz příkazové řádky
    """
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.teardown_appcontext(close_db_cur)
    app.cli.add_command(init_db_command)
