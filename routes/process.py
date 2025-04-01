from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from forms.form_info import ProcessForm
from utils.db import db
from models.process_model import Process, Table
from flask_login import  login_required, current_user
import matplotlib.pyplot as plt
import io
from flask import Response

process = Blueprint("process", __name__)

@process.route("/")
@process.route('/home')
def home():
    return render_template("home.html")


@process.route("/index", methods=["GET", "POST"])
@login_required
def index():
    form = ProcessForm()  # Ensure form is initialized
    selected_table_id = session.get("selected_table_id")

    # Get all tables for the current user
    tables = Table.query.filter_by(user_id=current_user.id).all()
    
    if not selected_table_id and tables:
        # Auto-select the first table if none is selected
        selected_table_id = tables[0].id
        session["selected_table_id"] = selected_table_id

    selected_table = Table.query.get(selected_table_id) if selected_table_id else None

    if request.method == "POST" and form.validate_on_submit():
        last_process = Process.query.filter_by(table_id=selected_table_id).order_by(Process.user_process_id.desc()).first()
        next_user_process_id = 1 if last_process is None else last_process.user_process_id + 1

        new_process = Process(
            user_process_id=next_user_process_id,
            name=form.name.data,
            duration=form.duration.data,
            operators=form.operators.data,
            cycle_time=form.cycle_time.data,
            units_produced=form.units_produced.data,
            setup_time=form.setup_time.data,
            downtime=form.downtime.data,
            user_id=current_user.id,
            table_id=selected_table_id,
            author=current_user.username
        )
        db.session.add(new_process)
        db.session.commit()
        reorder_ids(selected_table.id)
        flash("Process added successfully!", category="success")
        return redirect(url_for("process.index"))

    # 🔹 Ensure this return is always executed
    if request.method == "GET":
        efficiency = calculate_efficiency(selected_table_id) if selected_table else 0

        processes = Process.query.filter_by(table_id=selected_table_id).all() if selected_table else []

        process_efficiencies = {p.id: calculate_process_efficiency(p) for p in processes}

        return render_template("index.html", form=form, processes=processes, user=current_user, tables=tables, selected_table=selected_table, efficiency=efficiency, process_efficiencies=process_efficiencies)

@process.route("/create_table", methods=[ "GET", "POST"])
@login_required
def create_table():
    table_name = request.form.get("table_name")
    if table_name:
        new_table = Table(name=table_name, user_id=current_user.id)
        db.session.add(new_table)
        db.session.commit()
        flash(f"Table '{table_name}' created!", category="success")
    else:
        flash("Table could not be created!", category="danger")

    return redirect(url_for("process.index"))

@process.route("/select_table", methods=["GET", "POST"])
@login_required
def select_table():
    table_id = request.args.get("table_id")
    table = Table.query.filter_by(id=table_id, user_id=current_user.id).first()

    if table:
        session["selected_table_id"] = table.id
        flash(f"Switched to table '{table.name}'", category="info")
    else:
        flash("Table not found!", category="danger")

    return redirect(url_for("process.index"))

@process.route("/delete_table/<int:table_id>", methods=["GET", "POST"])
@login_required
def delete_table(table_id):
    table = Table.query.filter_by(id=table_id, user_id=current_user.id).first()
    if table:
        Process.query.filter_by(table_id=table.id).delete()
        db.session.delete(table)
        db.session.commit()
        flash(f"Table '{table.name}' deleted!", category="success")
        session.pop("selected_table_id", None)  # Remove selected table
    else:
        flash(f"Table '{table.name}' could not be deleted!", category="danger")
    return redirect(url_for("process.index"))

    
@process.route("/update/<int:id>", methods=["GET", "POST"])
@login_required
def update(id):
    process_1 = Process.query.get_or_404(id)
    form = ProcessForm(obj=process_1)
    if process_1.user_id == current_user.id:
        if request.method == "POST" and form.validate_on_submit():
            process_1.name = form.name.data
            process_1.duration = form.duration.data
            process_1.operators = form.operators.data
            process_1.cycle_time = form.cycle_time.data
            process_1.units_produced  = form.units_produced.data
            process_1.setup_time = form.setup_time.data
            process_1.downtime = form.downtime.data

            db.session.commit()
            efficiency = calculate_efficiency(process_1.table_id)
            flash(f"Process updated successfully! New Efficiency: {efficiency}%", category="success")


            return redirect(url_for("process.index"))
    
    return render_template("update.html", form=form, process=process_1, user=current_user)


@process.route("/delete_process/<int:id>", methods=["GET", "POST"])
@login_required
def delete_process(id):
    process_1 = Process.query.get_or_404(id)

    if process_1:
        table_id = process_1.table_id
        if process_1.user_id != current_user.id:
            flash("You are not allowed to delete this process!", category="danger")
            return redirect(url_for("process.index"))
        

        db.session.delete(process_1)
        db.session.commit()

        reorder_ids(table_id)
        efficiency = calculate_efficiency(table_id)
        flash(f"Process deleted! New Efficiency: {efficiency}%", category="success")        


    return redirect(url_for("process.index"))
    


def reorder_ids(table_id):
    """
    Reorders the `user_process_id` for a specific table so they remain sequential.
    """
    if table_id is None:
        return 
    processes = Process.query.filter_by(table_id=table_id).order_by(Process.user_process_id).all()

    new_id = 1
    for process in processes:
        process.user_process_id = new_id
        new_id += 1

    db.session.commit()
    new_efficiency = calculate_efficiency(table_id)
    flash(f"Efficiency updated: {new_efficiency}%", category="info")


def calculate_efficiency(table_id):
    processes = Process.query.filter_by(table_id=table_id).all()

    if not processes:
        return 0  # No processes = 0% efficiency

    # ✅ Compute total standard time
    total_standard_time = sum(p.cycle_time * p.units_produced for p in processes if calculate_process_efficiency(p) > 0)

    # ✅ Compute total actual time (excluding processes with 0% efficiency)
    total_actual_time = sum(
        (p.duration - p.downtime - p.setup_time) * p.operators
        for p in processes if calculate_process_efficiency(p) > 0
    )

    # ✅ Prevent division by zero
    if total_actual_time <= 0:
        return 0  

    # ✅ Compute Total Efficiency
    total_efficiency = (total_standard_time / total_actual_time) * 100

    # 🔹 Debugging: Print values to check calculation
    print(f"DEBUG - Table ID: {table_id}")
    print(f"DEBUG - Total Standard Time: {total_standard_time}")
    print(f"DEBUG - Total Actual Time: {total_actual_time}")
    print(f"DEBUG - Computed Efficiency: {total_efficiency}")

    return round(total_efficiency, 2)

def calculate_process_efficiency(process):
    if not process or process.duration <= 0 or process.operators <= 0 or process.units_produced <= 0:
        return 0  

    # ✅ Consideramos downtime y setup time en el tiempo real
    total_actual_time = (process.duration - process.downtime - process.setup_time) * process.operators
    standard_time = process.cycle_time * process.units_produced

    # ✅ Prevenir valores negativos o cálculos incorrectos
    if total_actual_time <= 0:
        return 0

    efficiency = (standard_time / total_actual_time) * 100

    return round(efficiency, 2)

def generate_efficiency_time_series_svg(processes):

    # Extract process names and efficiencies
    process_names = [process.name for process in processes]
    efficiencies = [calculate_process_efficiency(process) for process in processes]  # ✅ Ensure efficiency is always calculated

    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(8, 5))
    
    # Plot efficiency trend (line chart)
    ax.plot(process_names, efficiencies, marker='o', linestyle='-', color='blue', alpha=0.7, label="Efficiency (%)")

    # Labels and title
    ax.set_xlabel("Process Name (Order of Entry)", fontsize=12)
    ax.set_ylabel("Efficiency (%)", fontsize=12)
    ax.set_title("Efficiency Trend Per Process", fontsize=14, fontweight='bold')
    
    # Set Y-axis limit to avoid values above 100% (if needed)
    ax.set_ylim(0, 110)

    # Grid for better readability
    ax.grid(True, linestyle='--', alpha=0.6)

    # Rotate X labels for better readability
    plt.xticks(rotation=45, ha='right')

    # Add legend
    ax.legend()

    # Save the figure in a BytesIO object as SVG
    img_io = io.BytesIO()
    plt.savefig(img_io, format='svg', bbox_inches="tight")
    img_io.seek(0)
    
    return Response(img_io.getvalue(), mimetype="image/svg+xml")

@process.route("/efficiency_trend_svg")
@login_required
def efficiency_trend_svg():
    selected_table_id = session.get("selected_table_id")
    
    if not selected_table_id:
        flash("No table selected for efficiency graph.", "danger")
        return redirect(url_for("process.index"))

    processes = Process.query.filter_by(table_id=selected_table_id).all()

    if not processes:
        flash("No processes found for this table.", "danger")
        return redirect(url_for("process.index"))

    return generate_efficiency_time_series_svg(processes)
