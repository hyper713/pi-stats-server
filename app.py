from flask import Flask, request, jsonify
import sqlite3
import sys

app = Flask(__name__)
database='pi-stats.db'

@app.route('/')
def output():
    connection = sqlite3.connect(database)
    cursor=connection.cursor()

    cursor.execute("SELECT temp,rh,time FROM stats")
    rows=cursor.fetchall()

    connection.commit()
    connection.close()

    return jsonify({"temp": rows})

@app.route('/input', methods=['POST'])
def input():
    temperature = request.json['temp']
    humidity = request.json['rh']
    raspberry_time = request.json['time']

    connection = sqlite3.connect(database)
    cursor=connection.cursor()

    cursor.execute("INSERT INTO stats VALUES (?, ?, ?)", (temperature, humidity, raspberry_time))

    connection.commit()
    connection.close()

    return jsonify({"msg": "well inserted"})

@app.route('/reset')
def reset():
    connection = sqlite3.connect(database)
    cursor=connection.cursor()

    cursor.execute("DELETE FROM stats")
    cursor.execute("DELETE FROM log")

    connection.commit()
    connection.close()
    return jsonify({"msg": "Well reset"})

if __name__ == '__main__':
    app.run(debug=True)