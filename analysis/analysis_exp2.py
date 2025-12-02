import csv


def analyze():
    map = {
        "You are a precise recognizing textual entailment to": "RTE",
        "You are a precise natural language inference t": "MNLI",
        "You are a precise question-answer entailm": "QNLI",
        "You are a precise question paraphrase dete": "QQP",
        "You are a precise sentence sentimental": "SST",
    }
    count = {"SST": 0, "QQP": 0, "QNLI": 0, "MNLI": 0, "RTE": 0}
    ratios = {"SST": 0, "QQP": 0, "QNLI": 0, "MNLI": 0, "RTE": 0}
    data = {"SST": [], "QQP": [], "QNLI": [], "MNLI": [], "RTE": []}

    with open("../outputs/exp2_adversary_2025-12-01-21-46-35.csv", "r") as f:
        reader = csv.reader(f)
        for row in reader:
            for key, task in map.items():
                if key in row[2]:
                    data[task].append(row)
                    if row[4][0] == "T":
                        count[task] += 1
                    break

    for key in ratios.keys():
        ratios[key] = count[key] / len(data[key])

    print("Counts:", count)
    print("Ratios:", ratios)


analyze()
