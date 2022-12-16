import csv
import re
import numpy as np
import pandas as pd

# Add the column names in the DocsDB file in the correct order
col_names = [
    "Name",
    "Stu Id",
    "AI Q1",
    "Lab1",
    "Lab2",
    "Lab3",
    "Lab4",
    "Lab5",
    "Lab6",
    "Lab7",
    "Lab8",
    "Lab9",
    "Midt1",
    "Quiz1",
    "Quiz2",
    "Quiz3",
    "Quiz4",
    "Total",
]

# Define what counts as a low lab grade
lab_cutoff_threshold = 2


def read_data(file_name: str) -> list[str]:
    """Reads all the lines from the requested file

    Args:
        file_name (str): the address of the file to be read

    Returns:
        list[str]: list of lines read from the file
    """
    with open(file_name, "r") as fp:
        lines = fp.readlines()
        return lines


def clean_data(lines: list) -> list[dict]:
    """This function converts each string record to a key-value based dictionary.
    The keys come from the col_names variable defined at the top

    Args:
        lines (list): _description_

    Returns:
        list[dict]: _description_
    """
    records = []
    for line in lines:
        record = {}
        if len(line.split()) > 0:
            index_of_id = re.search(r"\d", line).start()
            name = line[:index_of_id].strip()
            record[col_names[0]] = name

            features = line[index_of_id:].split()
            for i in range(len(features)):
                # "-" indicates empty in DocsDB
                if features[i].strip() == "-":
                    record[col_names[i + 1]] = None
                else:
                    record[col_names[i + 1]] = features[i]
            records.append(record)
    return records


def is_lost(record: dict, not_submitted: list, roster_data: pd.DataFrame) -> bool:
    """Decides if the given student record is a lost student or not

    Args:
        record (dict): a student's features
        not_submitted (list): list of students that didn't submit (from eclass)
        roster_data (pd.DataFrame): Dataframe of roster information

    Returns:
        bool: True if the student is lost
    """
    if (
        (
            record["Lab8"] != "EA"
            and (
                (
                    record["Lab8"] is None
                    and get_ccid_by_id(roster_data, record["Stu Id"]) in not_submitted
                )
                or (
                    (
                        record["Lab8"] is not None
                        and float(record["Lab8"]) <= lab_cutoff_threshold
                    )
                )
            )
        )
        and (
            record["Lab7"] != "EA"
            and (
                record["Lab7"] is None or float(record["Lab7"]) <= lab_cutoff_threshold
            )
        )
        # This should be removed if it's still before the first midterm term
        # However, if it's past the midterm date and the student does not have
        # a midterm grade, we can't effectively help them catch up.
        and (record["Midt1"] is not None)
    ):
        return True
    return False


def find_quantile(df: pd.DataFrame, item: str, quantile: float) -> float:
    """Finds the nth qu

    Args:
        df (pd.DataFrame): the dataframe that contains all student info
        item (str): the item for which to calculate the quantile e.g. Quiz1
        quantile (float): one of [0.25, 0.5, 0.75]

    Returns:
        float: the value of the quantile for the specified item
    """
    nans_removed = df[df[item].notna()]
    EAs_removed = nans_removed[~(nans_removed[item] == "EA")][item]
    grades_column = np.array(EAs_removed, dtype=float)
    print(f"number of lost students who have a valid score: {grades_column.shape}")
    quantile = np.quantile(grades_column, quantile)
    print(f"quantile for these students: {quantile}")
    return quantile


def find_lost_students(
    records: list[dict], not_submitted: list, roster_data: pd.DataFrame
) -> list[dict]:
    """Returns the list of lost students

    Args:
        records (list[dict]): list of all student records
        not_submitted (list): the list of students that did not submit the last lab (from eClass)
        roster_data (pd.DataFrame): the information of the eClass roster

    Returns:
        list[dict]: list of lost student records
    """
    lost = []
    for record in records:
        if is_lost(record, not_submitted, roster_data):
            lost.append(record)
    return lost


def get_ccid_by_id(students: pd.DataFrame, id: str) -> str:
    """Returns the CCid of a student given their student ID

    Args:
        students (pd.DataFrame): the dataframe containing all student info
        id (str): student id

    Returns:
        str: student's CCID e.g. dummy@ualberta.ca
    """
    id = int(id)
    val = students[students["Stu Id"].isin([id])]["CCid"].values[0]
    return val


def write_lost_in_csv(lost_students: list[dict], lost_records_name: str) -> None:
    """Writes the lost students' information in a csv file

    Args:
        lost_students (list[dict]): the list of extracted lost students
        lost_records_name (str): the name of the file to write the data in
    """
    if lost_students:
        with open(lost_records_name, "w") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(col_names)
            for row in lost_students:
                writer.writerow([row[col_name] for col_name in col_names])


def merge_with_roster_and_reports(
    lost_records_name: str,
    reports_name: str,
    roster_data: pd.DataFrame,
    previous_name: str,
    final_name: str,
) -> None:
    lost_records: pd.DataFrame = pd.read_csv(lost_records_name)

    df_reports = pd.read_csv(reports_name)
    df_prev = pd.read_excel(previous_name)

    # Merge the two dataframes, using _ID column as key
    merged_with_roster = pd.merge(lost_records, roster_data, on="Stu Id")

    # Exclude those with Ok quiz grades (those with quiz grades better than Q1)
    q = find_quantile(merged_with_roster, "Quiz1", 0.25)
    merged_with_roster = merged_with_roster[merged_with_roster["Quiz4"] <= q]

    compare = df_reports["CCid"].tolist()

    merged_with_roster["contacted_before"] = (
        merged_with_roster["CCid"].isin(compare).astype(int)
    )

    df_reports = df_reports[["CCid", "Assigned TA", "Reason for reporting?"]]
    temp = pd.merge(merged_with_roster, df_reports, on="CCid", how="left")

    for index, row in temp.iterrows():
        if row["CCid"] in list(df_prev["CCid"]):
            print(
                row["CCid"],
            )
            print(
                df_prev.loc[df_prev["CCid"] == row["CCid"]]["Assigned TA"].tolist()[-1],
            )

            temp.at[index, "Assigned TA"] = df_prev.loc[df_prev["CCid"] == row["CCid"]][
                "Assigned TA"
            ].tolist()[-1]

            temp.at[index, "Reason for reporting?"] = "Extracted from DocsDB last week"
            temp.at[index, "contacted_before"] = 1
            print()

    temp = temp.loc[:, ~temp.columns.str.contains("^Unnamed")]  # remove unnamed columns
    temp.to_csv(final_name)
    temp.to_excel(final_name.replace(".csv", "") + ".xlsx")


def main():
    html_name = "docsdb_nov28.html"  # DocsDB Mark Posting HTML without the html tags
    to_create_lost_records_name = "today_losts_Nov28.csv"  # Name of the file to write lost students in before merging
    roster_name = "roster_nov28.csv"
    reports_name = "reports_nov28.csv"  # Reported students by the TAs
    previous_extracted = "list_9.xlsx"  # Last week's lost students file
    final_file_name = (
        "list_10.csv"  # Name of the final file to write the lost student records in
    )
    not_submitted = "not_submitted.csv"  # csv file containing all the students that didn't submit the last lab

    raw_data: list = read_data(html_name)
    cleaned_data: list = clean_data(raw_data)

    roster_data = pd.read_csv(roster_name)

    not_submitted = list(pd.read_csv(not_submitted)["CCid"])
    lost_students: list = find_lost_students(cleaned_data, not_submitted, roster_data)
    write_lost_in_csv(lost_students, to_create_lost_records_name)
    merge_with_roster_and_reports(
        to_create_lost_records_name,
        reports_name,
        roster_data,
        previous_extracted,
        final_file_name,
    )


main()
