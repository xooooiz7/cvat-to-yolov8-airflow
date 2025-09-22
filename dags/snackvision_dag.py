#airflow standalone
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

# ตั้งค่า DAG
with DAG(
    dag_id="snackvision_pipeline",
    start_date=datetime(2025, 9, 21),
    schedule=None,  # กด Trigger เอง ไม่ auto
    catchup=False,
    tags=["snackvision", "pipeline"],
) as dag:

    # 1. Change format
    change_format = BashOperator(
        task_id="change_format",
        bash_command="python3 /Users/sittasahathum/Desktop/airflow_snackvision/scripts/1_change_format.py"
    )

    # 2. Split
    split = BashOperator(
        task_id="split",
        bash_command="python3 /Users/sittasahathum/Desktop/airflow_snackvision/scripts/2_split.py"
    )

    # 3. Augment
    augment = BashOperator(
        task_id="augment",
        bash_command="python3 /Users/sittasahathum/Desktop/airflow_snackvision/scripts/3_augment.py"
    )

    # 4. Export
    export = BashOperator(
        task_id="export",
        bash_command="python3 /Users/sittasahathum/Desktop/airflow_snackvision/scripts/4_export.py"
    )

    # 5. Class Analysis
    class_analysis = BashOperator(
        task_id="class_analysis",
        bash_command="python3 /Users/sittasahathum/Desktop/airflow_snackvision/scripts/5_classanalysis.py"
    )

    # dependency chain
    change_format >> split >> augment >> export >> class_analysis
