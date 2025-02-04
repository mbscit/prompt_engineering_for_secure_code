import os
import csv

data_folder_path = os.path.dirname("./cwe_lists/")
# these files were used to get a complete list (except for CWE-730, which is a category):
# [disclaimer: maybe some of those lists were not necessary to complete the cwe set]
#
# 699.csv (https://cwe.mitre.org/data/csv/699.csv.zip)
# 1000.csv (https://cwe.mitre.org/data/csv/1000.csv.zip)
# 1194.csv (https://cwe.mitre.org/data/csv/1194.csv.zip)
# 1200.csv (https://cwe.mitre.org/data/csv/1200.csv.zip)
# 1337.csv (https://cwe.mitre.org/data/csv/1337.csv.zip)
# 1350.csv (https://cwe.mitre.org/data/csv/1350.csv.zip)
# 1387.csv (https://cwe.mitre.org/data/csv/1387.csv.zip)


cwe = {
    "CWE-1004": "",
    "CWE-113": "",
    "CWE-116": "",
    "CWE-117": "",
    "CWE-119": "",
    "CWE-120": "",
    "CWE-1204": "",
    "CWE-125": "",
    "CWE-1275": "",
    "CWE-1333": "",
    "CWE-14": "",
    "CWE-190": "",
    "CWE-193": "",
    "CWE-20": "",
    "CWE-200": "",
    "CWE-209": "",
    "CWE-215": "",
    "CWE-22": "",
    "CWE-250": "",
    "CWE-252": "",
    "CWE-259": "",
    "CWE-269": "",
    "CWE-276": "",
    "CWE-283": "",
    "CWE-285": "",
    "CWE-287": "",
    "CWE-295": "",
    "CWE-306": "",
    "CWE-319": "",
    "CWE-321": "",
    "CWE-326": "",
    "CWE-327": "",
    "CWE-328": "",
    "CWE-329": "",
    "CWE-330": "",
    "CWE-331": "",
    "CWE-339": "",
    "CWE-347": "",
    "CWE-367": "",
    "CWE-377": "",
    "CWE-379": "",
    "CWE-385": "",
    "CWE-400": "",
    "CWE-406": "",
    "CWE-414": "",
    "CWE-415": "",
    "CWE-416": "",
    "CWE-425": "",
    "CWE-434": "",
    "CWE-454": "",
    "CWE-462": "",
    "CWE-467": "",
    "CWE-476": "",
    "CWE-477": "",
    "CWE-489": "",
    "CWE-502": "",
    "CWE-521": "",
    "CWE-522": "",
    "CWE-595": "",
    "CWE-601": "",
    "CWE-605": "",
    "CWE-611": "",
    "CWE-614": "",
    "CWE-641": "",
    "CWE-643": "",
    "CWE-668": "",
    "CWE-676": "",
    "CWE-703": "",
    "CWE-704": "",
    "CWE-730": "",
    "CWE-732": "",
    "CWE-759": "",
    "CWE-760": "",
    "CWE-776": "",
    "CWE-78": "",
    "CWE-787": "",
    "CWE-79": "",
    "CWE-798": "",
    "CWE-80": "",
    "CWE-827": "",
    "CWE-835": "",
    "CWE-841": "",
    "CWE-89": "",
    "CWE-90": "",
    "CWE-915": "",
    "CWE-918": "",
    "CWE-939": "",
    "CWE-94": "",
    "CWE-941": "",
    "CWE-943": "",
    "CWE-95": "",
    "CWE-96": "",
    "CWE-99": "",
}

for file in os.listdir(data_folder_path):
    data_file_path = os.path.join(data_folder_path, file)
    # checking if it is a file
    if os.path.isfile(data_file_path):
        file_name, file_extension = os.path.splitext(data_file_path)
        with open(f"{file_name}{file_extension}", "r") as file:
            data = list(csv.reader(file))
        for row in data:
            cwe_id = f"CWE-{row[0]}"
            if cwe_id in cwe and cwe[cwe_id] == "":
                cwe[cwe_id] = f"CWE-{row[0]}, {row[1]}: {row[4]}"
            cwe_id_zero = f"CWE-0{row[0]}"
            if cwe_id_zero in cwe and cwe[cwe_id_zero] == "":
                cwe[cwe_id_zero] = f"CWE-{row[0]}, {row[1]}: {row[4]}"

for key in cwe:
    print(f'"{key}": "{cwe[key]}",')
