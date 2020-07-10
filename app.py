from flask import Flask, request, jsonify
import sqlite3
import sys
import time

app = Flask(__name__)
database = 'pi-stats.db'
app_key = "Wd8TrB3G36gf7pf"
separator = "|~|"


@app.route('/', methods=['GET'])
def output():
    rows = []
    try:
        connection = sqlite3.connect(database)
        cursor = connection.cursor()

        cursor.execute("SELECT temp,rh,time FROM stats")
        rows = cursor.fetchall()

        connection.commit()
        connection.close()

    except sqlite3.Error as e:
        file = open('log.txt', 'a')
        file.write(time.strftime("%Y-%m-%d %H:%M:%S") +
                   separator+"Database Error"+separator+"%s" % e)
        file.write('\n')
        file.close()
        return jsonify({"msg": "database error"})

    return jsonify({"temp": rows})


@app.route('/input', methods=['POST'])
def input():
    temperature = request.json['temp']
    humidity = request.json['rh']
    raspberry_time = request.json['time']
    key = request.json['key']

    if key == app_key:
        if temperature == "-" and humidity == "-":
            file = open('log.txt', 'a')
            file.write(raspberry_time+separator+"Sensor Error" +
                       separator+"sensor failure, check wiring")
            file.write('\n')
            file.close()
            return jsonify({"msg": "sensor error"})
        else:
            try:
                connection = sqlite3.connect(database)
                cursor = connection.cursor()

                cursor.execute("INSERT INTO stats VALUES (?, ?, ?)",
                               (temperature, humidity, raspberry_time))

                connection.commit()
                connection.close()

            except sqlite3.Error as e:
                file = open('log.txt', 'a')
                file.write(time.strftime("%Y-%m-%d %H:%M:%S") +
                           "|~|"+"Database Error"+separator+"%s" % e)
                file.write('\n')
                file.close()
                return jsonify({"msg": "database error"})

            return jsonify({"msg": "well inserted"})
    else:
        return jsonify({"msg": "bad key"})


@app.route('/reset', methods=['POST'])
def reset():
    key = request.json['key']

    if key == app_key:
        try:
            connection = sqlite3.connect(database)
            cursor = connection.cursor()

            cursor.execute("DELETE FROM stats")

            connection.commit()
            connection.close()

        except sqlite3.Error as e:
            file = open('log.txt', 'a')
            file.write(time.strftime("%Y-%m-%d %H:%M:%S") +
                       separator+"Database Error"+separator+"%s" % e)
            file.write('\n')
            file.close()
            return jsonify({"msg": "database error"})

        file = open('log.txt', 'a')
        file.write(time.strftime("%Y-%m-%d %H:%M:%S")+separator +
                   "Database Reset"+separator+"database reset succeed")
        file.write('\n')
        file.close()
        return jsonify({"msg": "Well reset"})
    else:
        return jsonify({"msg": "bad key"})


if __name__ == '__main__':
    app.run(host='192.168.1.127', debug=True)
