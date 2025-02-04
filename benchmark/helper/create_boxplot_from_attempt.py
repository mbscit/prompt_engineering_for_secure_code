from operator import itemgetter
import os
import sys
import statistics

from dotenv import load_dotenv

sys.path.append("../sec_prompt_benchmark")

import utils

load_dotenv()
data_folder_path = os.path.dirname(
    utils.relative_path_from_root(os.getenv("DATA_FILE_PATH"))
)

stats = []

for file in os.listdir(data_folder_path):
    data_file_path = os.path.join(data_folder_path, file)
    # checking if it is a file
    if os.path.isfile(data_file_path):
        approach = utils.read_approaches_file(data_file_path)
        stats.append(
            {
                "id": approach.id.replace("_", "\_").replace("iteration", "iter"),
                "median": statistics.median(
                    approach.scanners_agree_sample_filtered_vulnerable_percentages
                ),
                "min": min(
                    approach.scanners_agree_sample_filtered_vulnerable_percentages
                ),
                "max": max(
                    approach.scanners_agree_sample_filtered_vulnerable_percentages
                ),
                "quartiles": statistics.quantiles(
                    approach.scanners_agree_sample_filtered_vulnerable_percentages
                ),
                "avg": approach.scanners_agree_filtered_vulnerable_percentage,
            }
        )

stats = sorted(stats, key=itemgetter("avg"), reverse=True)

print(
    """\\begin{figure}[htbp]
\\begin{center}
\\begin{tikzpicture}
\\begin{axis}
    [
    cycle list={{purple},{blue},{black},{darkgray},{violet},{brown}},
    height=.7\\textheight,
    width=.7\\textwidth,
    xlabel=Vulnerable Percentage,"""
)
print("    ytick={", end="")

end = len(stats)
for id, stat in enumerate(stats, start=1):
    print(id, end="")
    if id != end:
        print(",", end="")
print("},")
print("    yticklabels={", end="")

for id, stat in enumerate(stats, start=1):
    print(stat.get("id"), end="")
    if id != end:
        print(",", end="")
print("},")
print("    ]")

for id, stat in enumerate(stats, start=1):
    print(
        f"""    \\addplot+[
    boxplot prepared={{
        median={stat.get("median"):.3f},
        upper quartile={stat.get("quartiles")[2]:.3f},
        lower quartile={stat.get("quartiles")[0]:.3f},
        upper whisker={stat.get("max"):.3f},
        lower whisker={stat.get("min"):.3f}
    }},
    ] coordinates {{({id},{stat.get("avg"):.3f})}};"""
    )

print("  \end{axis}")
print("\end{tikzpicture}")
print(
    f"""\end{{center}}
\caption{{Vulnerability Distribution per Attempt {data_folder_path.replace(".", "").replace("/", "").replace("35", "3.5-turbo").replace("data", "GPT")}}}
\label{{fig:vulnerability_distribution_per_attempt_{data_folder_path.replace(".", "").replace("/", "").replace("35", "3.5-turbo").replace("data", "gpt")}}}
\end{{figure}}"""
)
