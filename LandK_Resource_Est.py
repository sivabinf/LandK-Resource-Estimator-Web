
from flask import Flask, request, render_template_string
import math

app = Flask(__name__)


def LandK_Resource_Estimation(
    Query,
    Current_Resource,
    Production_Rate,
    Target_Production=0,
    Target_Time=0
):
    # Query 0: Calculate Projected Time
    if Query == 0:

        Resource_Diff = Target_Production - Current_Resource

        if Resource_Diff <= 0:
            return 0

        if Production_Rate <= 0:
            raise ValueError("Production rate must be greater than zero.")

        return Resource_Diff / Production_Rate

    # Query 1: Calculate Projected Resource
    elif Query == 1:

        if Target_Time < 0:
            raise ValueError("Time cannot be negative.")

        return Current_Resource + (
            Production_Rate * Target_Time
        )

    else:
        raise ValueError("Invalid calculation type.")


HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>LandK Resource Estimator</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        * { box-sizing: border-box; }

        body {
            margin: 0;
            padding: 30px 15px;
            font-family: Arial, sans-serif;
            background: #101827;
            color: white;
        }

        .container {
            max-width: 600px;
            margin: 40px auto;
            padding: 30px;
            background: #1c293b;
            border-radius: 16px;
            box-shadow: 0 10px 35px #0005;
        }

        h1 { color: #65d6a5; }

        p { color: #aab8ca; }

        label {
            display: block;
            margin: 18px 0 7px;
            font-weight: bold;
        }

        input, select {
            width: 100%;
            padding: 13px;
            border: 1px solid #40516a;
            border-radius: 8px;
            background: #101827;
            color: white;
            font-size: 16px;
        }

        button {
            width: 100%;
            margin-top: 25px;
            padding: 15px;
            border: none;
            border-radius: 8px;
            background: #28b77a;
            color: white;
            font-size: 17px;
            font-weight: bold;
            cursor: pointer;
        }

        button:hover { background: #209b67; }

        .result {
            margin-top: 25px;
            padding: 20px;
            border-radius: 10px;
            background: #123c32;
            border: 1px solid #28b77a;
        }

        .error {
            background: #49252c;
            border-color: #e66b75;
        }

        .value {
            font-size: 32px;
            font-weight: bold;
            color: #65d6a5;
            overflow-wrap: anywhere;
        }

        .hint {
            font-size: 13px;
            margin-top: 7px;
        }
    </style>
</head>

<body>
<div class="container">

    <h1>LandK Resource Estimator</h1>

    <p>
        Estimate production time or calculate future resource levels.
    </p>

    <form method="POST">

        <label>Calculation Type</label>

        <select name="query" id="query" onchange="updateLabel()">
            <option value="0"
                {% if query == 0 %}selected{% endif %}>
                Projected Time
            </option>

            <option value="1"
                {% if query == 1 %}selected{% endif %}>
                Projected Resource
            </option>
        </select>

        <label>Current Resource</label>

        <input type="number"
               step="any"
               name="current_resource"
               value="{{ current or '' }}"
               placeholder="Enter current resource"
               required>

        <label>Production Rate (per hour)</label>

        <input type="number"
               step="any"
               name="production_rate"
               value="{{ rate or '' }}"
               placeholder="Enter production rate"
               required>

        <div id="productionTarget">
            <label>Target Resource</label>
            <input type="number"
            step="any"
            name="target_production"
            value="{{ target_production if target_production is not none else '' }}"
            placeholder="Enter target resource"
            required>
        </div>

        <p class="hint" id="hint">
            Enter the resource level you want to reach.
        </p>
		
		<div id="timeTarget">
            <label>Target Time</label>
            <input type="number"
            step="any"
            name="target_time"
            value="{{ target_time if target_time is not none else '' }}"
            placeholder="Enter target time"
            required>
        </div>

        <p class="hint" id="hint">
            Enter the time period to calculate the resource level.
        </p>	
		

        <button type="submit">Calculate Results</button>

    </form>

    {% if result is not none %}

        <div class="result {% if error %}error{% endif %}">

            <h2>
                {% if error %}
                    Calculation Error
                {% else %}
                    Your Results
                {% endif %}
            </h2>

            <div class="value">{{ result }}</div>

            {% if not error %}
                <p>{{ description }}</p>
            {% endif %}

        </div>

    {% endif %}

</div>

<script>
function updateLabel() {
    const query = document.getElementById("query").value;
    const label = document.getElementById("targetLabel");
    const hint = document.getElementById("hint");

    if (query === "0") {
        label.innerText = "Target Resource";
        hint.innerText = "Enter the resource level you want to reach.";
    } else {
        label.innerText = "Time (Hours)";
        hint.innerText = "Enter how many hours into the future to calculate.";
    }
}

updateLabel();
</script>

</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def home():

    result = None
    error = False
    description = ""

    query = 0
    current = None
    rate = None
    target_production = None
    target_time = None

    if request.method == "POST":

        try:
            query = int(request.form["query"])
            current = float(request.form["current_resource"])
            rate = float(request.form["production_rate"])
            target_production = float(request.form["target_production"])
            target_time = float(request.form["target_time"])

            values = [current, rate, target_production, target_time]

            if not all(math.isfinite(v) for v in values):
                raise ValueError("Please enter valid finite numbers.")

            if current < 0:
                raise ValueError("Current resource cannot be negative.")

            if rate < 0:
                raise ValueError("Production rate cannot be negative.")

            answer = LandK_Resource_Estimation(
                query,
                current,
                rate,
                target_production,
				target_time
            )

            if query == 0:
                result = f"{answer:,.2f} hours"
                description = "Estimated time to reach your target resource."

            elif query == 1:
                result = f"{answer:,.2f} resource"
                description = f"Projected resource after {target_time:g} hours."

        except (ValueError, NotImplementedError) as e:
            result = str(e)
            error = True

    return render_template_string(
        HTML,
        result=result,
        error=error,
        description=description,
        query=query,
        current=current,
        rate=rate,
        target_production=target_production,
		target_time=target_time
    )


if __name__ == "__main__":
    app.run(debug=False)
