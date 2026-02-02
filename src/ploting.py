import argparse
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons

evaluators = {"Greedy", "Altroist", "Max_G/R", "Min-Min", "Min-Max", "Min-Sum", "Min-Avg", "Min-Abs", "Max-Min-Improvement", "Max-Avg-Improvement", "Max-Min-G/R"}
greedy_evaluators = ["Greedy", "Altroist", "Max_G/R"]
relevant = ["Min-Max", "Min-Sum", "Max-Min-Improvement", "Max-Avg-Improvement"]
values = non_greedy_keys = set(evaluators) - set(greedy_evaluators)

def main():
    parser = argparse.ArgumentParser(description="Plot with interactive checkboxes")
    parser.add_argument("filename", help="CSV file path")
    args = parser.parse_args()

    try:
        df = pd.read_csv(args.filename)
        df = df.sort_values(by='Min-Max - Min-Max')
        print(list(df["Min-Max - Min-Max"]))
    except Exception as e:
        print(f"Failed to read file: {e}")
        return

    for val in relevant:
        fig, ax = plt.subplots()
        plt.subplots_adjust(left=0.3)

        lines = []
        labels = []
        xs=list(range(len(df["Min-Max - Min-Max"])))
        for column in df.columns:
            if column.endswith(" - " + val) and any(column.startswith(prefix) for prefix in relevant):
                plt.scatter(xs, list(df[column]), label=column)
                # line, = ax.plot(list(df[column]), label=column)
                # lines.append(line)
                # labels.append(column)

        if not lines:
            continue
        plt.xlabel('X-axis')
        plt.ylabel('Y-axis')
        plt.title('Multiple Scatter Series')
        plt.legend()
        plt.show()
        # ax.set_title(f"{val}")
        # ax.set_xlabel("Index")
        # ax.set_ylabel("Value")

        # Checkbox position
        rax = plt.axes([0.05, 0.4, 0.2, 0.5])
        visibility = [True] * len(lines)
        check = CheckButtons(rax, labels, visibility)

        def toggle(label):
            index = labels.index(label)
            lines[index].set_visible(not lines[index].get_visible())
            plt.draw()

        check.on_clicked(toggle)

        plt.show()

if __name__ == "__main__":
    main()
