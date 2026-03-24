import os
from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

app = Flask(__name__)
CORS(app)

DB_URL = URL.create(
    drivername="mysql+pymysql",
    username=os.environ.get("DB_USERNAME"),
    password=os.environ.get("DB_PASSWORD"),
    host=os.environ.get("DB_HOST"),
    port=int(os.environ.get("DB_PORT", 10405)),
    database=os.environ.get("DB_NAME", "defaultdb")
)
engine = create_engine(DB_URL, connect_args={"ssl": {"ssl_disabled": False}})

def query(sql):
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        keys = result.keys()
        return [dict(zip(keys, row)) for row in result]

@app.route('/')
def index():
    return jsonify({"status": "Hospital KPI API is running ✅"})

@app.route('/api/kpi')
def kpi():
    rows = query("""
        SELECT
            ROUND(SUM(total_revenue), 2)          AS total_revenue,
            COUNT(*)                               AS total_patients,
            ROUND(AVG(wait_time_mins), 2)          AS avg_wait,
            ROUND(AVG(total_revenue), 2)           AS avg_rev_per_patient,
            ROUND(SUM(medication_revenue), 2)      AS total_medication,
            ROUND(SUM(lab_cost), 2)                AS total_lab,
            ROUND(SUM(consultation_revenue), 2)    AS total_consultation
        FROM hospital_kpi
    """)
    return jsonify(rows[0])

@app.route('/api/daily')
def daily():
    rows = query("""
        SELECT DATE_FORMAT(date,'%b %d') AS day,
               ROUND(SUM(total_revenue),2) AS revenue,
               COUNT(*) AS patients,
               ROUND(AVG(wait_time_mins),2) AS avg_wait
        FROM hospital_kpi GROUP BY date ORDER BY date
    """)
    return jsonify(rows)

@app.route('/api/doctor')
def doctor():
    rows = query("""
        SELECT doctor_type,
               ROUND(SUM(medication_revenue),2)   AS medication,
               ROUND(SUM(lab_cost),2)             AS lab,
               ROUND(SUM(consultation_revenue),2) AS consultation,
               ROUND(SUM(total_revenue),2)        AS total
        FROM hospital_kpi GROUP BY doctor_type ORDER BY total DESC
    """)
    return jsonify(rows)

@app.route('/api/financial')
def financial():
    rows = query("""
        SELECT financial_class,
               ROUND(SUM(total_revenue),2) AS total,
               COUNT(*) AS patients
        FROM hospital_kpi GROUP BY financial_class ORDER BY total DESC
    """)
    return jsonify(rows)

@app.route('/api/waittime')
def waittime():
    rows = query("""
        SELECT DATE_FORMAT(date,'%b %d') AS day,
               ROUND(AVG(wait_time_mins),2) AS avg_wait
        FROM hospital_kpi GROUP BY date ORDER BY date
    """)
    return jsonify(rows)

if __name__ == '__main__':
    app.run(debug=False)
