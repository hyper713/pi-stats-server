from flask import Flask, request, jsonify ,render_template
import sqlite3
import sys
import time

app = Flask(__name__)
database = 'pi-stats.db'
app_key = "Wd8TrB3G36gf7pf"
separator = "|~|"

@app.route('/', methods=['GET'])
def index():
    recent=[]
    try:
        connection = sqlite3.connect(database)

        cursor1 = connection.cursor()
        cursor1.execute("SELECT * FROM stats ORDER BY time DESC LIMIT 1")
        recent = cursor1.fetchone()

        cursor2 = connection.cursor()
        cursor2.execute("SELECT ROUND(AVG(temp), 2), ROUND(AVG(rh), 2), DATE(time) FROM stats GROUP BY DATE(time)")
        rows = cursor2.fetchall()

        connection.commit()
        connection.close()

    except sqlite3.Error as e:
        file = open('log.txt', 'a')
        file.write(time.strftime("%Y-%m-%d %H:%M:%S") +
                   separator+"Database Error"+separator+"%s" % e)
        file.write('\n')
        file.close()
        return jsonify({"msg": "database error"})

    temps, rhs, dates = [], [], []

    for i in range(len(rows)):
        temps.append(rows[i][0])
        rhs.append(rows[i][1])
        dates.append(rows[i][2])

    if recent is None :
        return render_template('index.html', temp='0', rh='0', time='0000-00-00 00:00:00', temps='', rhs='', dates='')

    return render_template('index.html', temp=recent[0], rh=recent[1], time=recent[2], temps=temps, rhs=rhs, dates=dates)

@app.route('/output', methods=['GET'])
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

    return jsonify(rows)


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
        file.write(time.strftime("%Y-%m-%d %H:%M:%S")+separator +"Database Reset"+separator+"database reset succeed")
        file.write('\n')
        file.close()
        return jsonify({"msg": "Well reset"})
    else:
        return jsonify({"msg": "bad key"})


if __name__ == '__main__':
    app.run(host='192.168.1.127', debug=True)
