import json

THRESHOLDS = {
    "bugs": [(0.05, "A"), (0.1, "B"), (0.2, "C"), (0.3, "D")],  # (Upper bound, Grade)
    "difficulty": [(10, "A"), (20, "B"), (30, "C"), (40, "D")],
    "effort": [(1000, "A"), (2000, "B"), (5000, "C"), (10000, "D")],
    "time": [(50, "A"), (100, "B"), (200, "C"), (500, "D")],
}


def evaluate_metric(value: float, metric: str, thresholds: dict = THRESHOLDS) -> str:
    """
    Evaluate a value against the thresholds of a specific metric.

    Args:
        value (float): The value to be graded.
        metric (str): The name of the metric (e.g., "bugs", "difficulty").
        thresholds (dict): A dictionary of thresholds for all metrics.

    Returns:
        str: The grade (A, B, C, D, F).
    """
    if metric not in thresholds:
        raise ValueError(f"Unknown metric: {metric}")

    if value < 0:
        return "ERR"  # Handle invalid values
    for upper_bound, grade in thresholds[metric]:
        if value <= upper_bound:
            return grade
    return "F"  # F is the default grade if no thresholds matched


def grade_metrics(value_dict: dict) -> dict:
    """
    Grade multiple metrics.

    Args:
        value_dict (dict): A dictionary of metrics and their respective values.
            Example: {'bugs': 0.12, 'difficulty': 25, 'effort': 3400, 'time': 80}

    Returns:
        dict: A dictionary of metrics and their respective grades.
            Example: {'bugs': 'B', 'difficulty': 'C', 'effort': 'C', 'time': 'B'}
    """
    return {metric: evaluate_metric(value, metric) for metric, value in value_dict.items()}


def transform_keys(obj, search_prefix, replace_with=""):
    """
    Recursively transform keys in a JSON object.

    Args:
        obj: The JSON object (dict, list, or primitive value)
        search_prefix: The prefix to search for in keys
        replace_with: The string to replace the prefix with (default: empty string)

    Returns:
        Transformed object with keys replaced
    """
    if isinstance(obj, dict):
        new_obj = {}
        for key, value in obj.items():
            # Transform the key if it starts with the search prefix
            new_key = key.replace(search_prefix, replace_with) if isinstance(key, str) and key.startswith(
                search_prefix) else key
            # Recursively process the value
            new_obj[new_key] = transform_keys(value, search_prefix, replace_with)
        return new_obj
    elif isinstance(obj, list):
        # Process each item in the list
        return [transform_keys(item, search_prefix, replace_with) for item in obj]
    else:
        # Return primitive values as is
        return obj


def load_json(file):
    with open(file, "r") as f:
        json_data = json.load(f)
    json_data = transform_keys(json_data, "../src/ten8t/", "")
    return json_data


def mi_to_table(file="radon_mi.json"):
    with open("radon_mi.json", 'r') as f:
        jd = json.load(f)
        with open("snippets/radon_mi.csv", "w") as of:
            of.write("File,Maint. Index,Rank")
            for k, v in jd.items():
                k = k.split("/")[-1]
                of.write(f"\n{k},{v['mi']:.1f},{v['rank']}")


def cc_to_table(file="radon_cc.json"):
    """
    The complexity json is
    1) List of filename key|array
    2) Relevant items in array items are:
          "type"
          "rank"
          "name"
          "complexity

    """
    with open(file, 'r') as f:
        jd = json.load(f)
        with open('snippets/radon_cc.csv', "w") as of:
            of.write("File,Name,Rank,Complexity\n")
            for k, v in jd.items():

                # v is a list of objects
                for item in v:
                    fname = k.split("/")[-1]
                    try:
                        if item['type'] == 'class':
                            of.write(f"{fname},{item['name']},{item['rank']},{item['complexity']:.1f}\n")
                    except:
                        print(f"Error with {k}")


def bug_thresh(value: float) -> str:
    if value <= 0.05:
        return 'A'
    elif value <= 0.1:
        return 'B'
    elif value <= 0.2:
        return 'C'
    elif value <= 0.3:
        return 'D'
    else:
        return 'F'


def difficulty_thresh(value: float) -> str:
    if value <= 10.0:
        return 'A'
    elif value <= 20:
        return 'B'
    elif value <= 30:
        return 'C'
    elif value <= 40:
        return 'D'
    else:
        return 'F'


def effort_thresh(value: float) -> str:
    if value <= 1000.0:
        return 'A'
    elif value <= 2000:
        return 'B'
    elif value <= 5000:
        return 'C'
    elif value <= 10000:
        return 'D'
    else:
        return 'F'


def time_thresh(value: float) -> str:
    if value <= 50.0:
        return 'A'
    elif value <= 100:
        return 'B'
    elif value <= 200:
        return 'C'
    elif value <= 5000:
        return 'D'
    else:
        return 'F'


def hal_to_table(input_file="radon_hal.json", output_file="radon_hal.csv"):
    """
    Process Halstead metrics and include grades in CSV output.
    """
    try:
        with open(input_file, "r") as f:
            jd = json.load(f)

        with open(output_file, "w") as of:
            columns = ["file", "bugs", "difficulty", "effort", "time"]
            grade_columns = [f"{col}_rank" for col in columns if col != "file"]
            all_cols = [col.title() for col in columns + grade_columns]
            of.write(",".join(all_cols) + "\n")

            for fname, data in jd.items():
                short_fname = fname.split("/")[-1]

                # Only taking file level metrics
                if "total" in data:
                    metrics = {col: float(data["total"][col]) for col in columns if col != "file"}
                    grades = grade_metrics(metrics)
                    numeric_values = [f"{metrics[col]}" for col in metrics]
                    grade_values = [grades[col] for col in metrics]
                    row = ",".join([short_fname] + numeric_values + grade_values)
                    of.write(f"{row}\n")

    except Exception as e:
        print(f"Error processing HAL metrics: {e}")


cc_to_table()
hal_to_table()
mi_to_table()
