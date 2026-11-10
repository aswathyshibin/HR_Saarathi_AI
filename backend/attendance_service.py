import pandas as pd

from datetime import datetime, date


# =========================================================
# DATE HELPERS
# =========================================================

def prepare_dataframe(df):
    """
    Clean and prepare attendance dataframe.
    """

    if df is None:
        return pd.DataFrame()

    if df.empty:
        return pd.DataFrame()

    df = df.copy()

    # -----------------------------------------------------
    # Clean column names
    # -----------------------------------------------------

    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    # -----------------------------------------------------
    # Clean string columns
    # -----------------------------------------------------

    for column in df.columns:

        if df[column].dtype == "object":

            df[column] = (
                df[column]
                .fillna("")
                .astype(str)
                .str.strip()
            )

    # -----------------------------------------------------
    # Date
    # -----------------------------------------------------

    if "Date" in df.columns:

        df["_Date"] = pd.to_datetime(
            df["Date"],
            dayfirst=True,
            errors="coerce"
        )

    return df


# =========================================================
# PERIOD FILTER
# =========================================================

def filter_by_period(
    df,
    period,
    date_from=None,
    date_to=None
):
    """
    Filter attendance data according to the
    period returned by Groq.
    """

    if df.empty:
        return df

    if "_Date" not in df.columns:
        return df

    today = pd.Timestamp(
        datetime.now().date()
    )

    # -----------------------------------------------------
    # TODAY
    # -----------------------------------------------------

    if period == "today":

        return df[
            df["_Date"].dt.date
            == today.date()
        ]


    # -----------------------------------------------------
    # YESTERDAY
    # -----------------------------------------------------

    if period == "yesterday":

        yesterday = (
            today -
            pd.Timedelta(days=1)
        )

        return df[
            df["_Date"].dt.date
            == yesterday.date()
        ]


    # -----------------------------------------------------
    # THIS WEEK
    # -----------------------------------------------------

    if period == "this_week":

        start = (
            today -
            pd.Timedelta(
                days=today.weekday()
            )
        )

        end = (
            start +
            pd.Timedelta(days=6)
        )

        return df[
            (df["_Date"] >= start) &
            (df["_Date"] <= end)
        ]


    # -----------------------------------------------------
    # THIS MONTH
    # -----------------------------------------------------

    if period == "this_month":

        start = pd.Timestamp(
            today.year,
            today.month,
            1
        )

        if today.month == 12:

            end = pd.Timestamp(
                today.year + 1,
                1,
                1
            ) - pd.Timedelta(days=1)

        else:

            end = pd.Timestamp(
                today.year,
                today.month + 1,
                1
            ) - pd.Timedelta(days=1)

        return df[
            (df["_Date"] >= start) &
            (df["_Date"] <= end)
        ]


    # -----------------------------------------------------
    # LAST MONTH
    # -----------------------------------------------------

    if period == "last_month":

        first_this_month = pd.Timestamp(
            today.year,
            today.month,
            1
        )

        last_day_previous = (
            first_this_month -
            pd.Timedelta(days=1)
        )

        first_previous = pd.Timestamp(
            last_day_previous.year,
            last_day_previous.month,
            1
        )

        return df[
            (df["_Date"] >= first_previous) &
            (df["_Date"] <= last_day_previous)
        ]


    # -----------------------------------------------------
    # THIS YEAR
    # -----------------------------------------------------

    if period == "this_year":

        start = pd.Timestamp(
            today.year,
            1,
            1
        )

        end = pd.Timestamp(
            today.year,
            12,
            31
        )

        return df[
            (df["_Date"] >= start) &
            (df["_Date"] <= end)
        ]


    # -----------------------------------------------------
    # CUSTOM DATE RANGE
    # -----------------------------------------------------

    if period == "custom":

        if date_from:

            start = pd.to_datetime(
                date_from,
                errors="coerce"
            )

        else:

            start = df["_Date"].min()


        if date_to:

            end = pd.to_datetime(
                date_to,
                errors="coerce"
            )

        else:

            end = df["_Date"].max()


        if pd.isna(start):
            start = df["_Date"].min()

        if pd.isna(end):
            end = df["_Date"].max()


        return df[
            (df["_Date"] >= start) &
            (df["_Date"] <= end)
        ]


    # -----------------------------------------------------
    # ALL TIME
    # -----------------------------------------------------

    return df


# =========================================================
# STATUS FILTER
# =========================================================

def filter_by_status(
    df,
    status
):
    """
    Filter Present / Absent / Leave / Late.
    """

    if df.empty:
        return df

    if not status:
        return df

    if "Status" not in df.columns:
        return df

    return df[
        df["Status"]
        .astype(str)
        .str.strip()
        .str.lower()
        ==
        str(status).strip().lower()
    ]


# =========================================================
# EMPLOYEE FILTER
# =========================================================

def filter_by_employee(
    df,
    employee_name
):

    if df.empty:
        return df

    if not employee_name:
        return df

    if "Employee_Name" not in df.columns:
        return df

    name = str(
        employee_name
    ).strip().lower()

    return df[
        df["Employee_Name"]
        .astype(str)
        .str.strip()
        .str.lower()
        .eq(name)
    ]


# =========================================================
# DEPARTMENT FILTER
# =========================================================

def filter_by_department(
    df,
    department
):

    if df.empty:
        return df

    if not department:
        return df

    if "Department" not in df.columns:
        return df

    dept = str(
        department
    ).strip().lower()

    return df[
        df["Department"]
        .astype(str)
        .str.strip()
        .str.lower()
        .eq(dept)
    ]


# =========================================================
# RECORD CONVERSION
# =========================================================

def records_from_dataframe(df):

    if df.empty:
        return []

    output = []

    for _, row in df.iterrows():

        record = {}

        for column in df.columns:

            # Internal helper column
            if column.startswith("_"):
                continue

            value = row[column]

            if pd.isna(value):
                value = ""

            elif isinstance(
                value,
                pd.Timestamp
            ):

                value = value.strftime(
                    "%Y-%m-%d"
                )

            else:

                value = str(value)

            record[column] = value

        output.append(record)

    return output


# =========================================================
# ATTENDANCE PERCENTAGE
# =========================================================

def calculate_attendance_percentage(
    df
):

    if df.empty:
        return 0.0

    if "Status" not in df.columns:
        return 0.0

    total = len(df)

    if total == 0:
        return 0.0

    present = len(
        df[
            df["Status"]
            .astype(str)
            .str.strip()
            .str.lower()
            == "present"
        ]
    )

    percentage = (
        present /
        total
    ) * 100

    return round(
        percentage,
        2
    )


# =========================================================
# DEPARTMENT SUMMARY
# =========================================================

def department_summary(
    df
):

    if df.empty:
        return []

    if "Department" not in df.columns:
        return []

    summary = []

    grouped = df.groupby(
        "Department"
    )

    for department, group in grouped:

        total = len(group)

        present = len(
            group[
                group["Status"]
                .astype(str)
                .str.lower()
                == "present"
            ]
        )

        absent = len(
            group[
                group["Status"]
                .astype(str)
                .str.lower()
                == "absent"
            ]
        )

        leave = len(
            group[
                group["Status"]
                .astype(str)
                .str.lower()
                == "leave"
            ]
        )

        summary.append({

            "department":
                str(department),

            "total_records":
                total,

            "present":
                present,

            "absent":
                absent,

            "leave":
                leave
        })

    return summary


# =========================================================
# MAIN ANALYSIS FUNCTION
# =========================================================

def analyze_attendance(
    df,
    query
):
    """
    Main attendance analysis function.

    IMPORTANT:
    This accepts TWO arguments:

        df
        query

    because main.py calls:

        analyze_attendance(df, query)
    """

    # -----------------------------------------------------
    # Prepare data
    # -----------------------------------------------------

    working_df = prepare_dataframe(
        df
    )

    if working_df.empty:

        return {

            "success": True,

            "message":
                "No attendance data available.",

            "count": 0,

            "records": [],

            "statistics": {}

        }


    # -----------------------------------------------------
    # Read query
    # -----------------------------------------------------

    if query is None:
        query = {}


    intent = query.get(
        "intent",
        "unknown"
    )

    period = query.get(
        "period",
        "all_time"
    )

    employee_name = query.get(
        "employee_name"
    )

    department = query.get(
        "department"
    )

    status = query.get(
        "status"
    )

    date_from = query.get(
        "date_from"
    )

    date_to = query.get(
        "date_to"
    )


    # -----------------------------------------------------
    # Period
    # -----------------------------------------------------

    filtered_df = filter_by_period(

        working_df,

        period,

        date_from,

        date_to

    )


    # -----------------------------------------------------
    # Employee
    # -----------------------------------------------------

    filtered_df = filter_by_employee(

        filtered_df,

        employee_name

    )


    # -----------------------------------------------------
    # Department
    # -----------------------------------------------------

    filtered_df = filter_by_department(

        filtered_df,

        department

    )


    # -----------------------------------------------------
    # Status
    # -----------------------------------------------------

    filtered_df = filter_by_status(

        filtered_df,

        status

    )


    # -----------------------------------------------------
    # Records
    # -----------------------------------------------------

    records = records_from_dataframe(
        filtered_df
    )


    # -----------------------------------------------------
    # Statistics
    # -----------------------------------------------------

    total = len(
        filtered_df
    )


    present = 0
    absent = 0
    leave = 0
    late = 0


    if not filtered_df.empty:

        if "Status" in filtered_df.columns:

            status_series = (
                filtered_df["Status"]
                .astype(str)
                .str.strip()
                .str.lower()
            )

            present = int(
                (status_series == "present")
                .sum()
            )

            absent = int(
                (status_series == "absent")
                .sum()
            )

            leave = int(
                (status_series == "leave")
                .sum()
            )

            late = int(
                (status_series == "late")
                .sum()
            )


    # -----------------------------------------------------
    # Attendance percentage
    # -----------------------------------------------------

    attendance_percentage = (
        calculate_attendance_percentage(
            filtered_df
        )
    )


    # -----------------------------------------------------
    # Employee names
    # -----------------------------------------------------

    employee_names = []

    if (
        not filtered_df.empty
        and
        "Employee_Name"
        in filtered_df.columns
    ):

        employee_names = (
            filtered_df[
                "Employee_Name"
            ]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
            .tolist()
        )


    # -----------------------------------------------------
    # Department summary
    # -----------------------------------------------------

    dept_summary = (
        department_summary(
            filtered_df
        )
    )


    # -----------------------------------------------------
    # Return verified result
    # -----------------------------------------------------

    return {

        "success": True,

        "intent":
            intent,

        "period":
            period,

        "employee_name":
            employee_name,

        "department":
            department,

        "status":
            status,

        "count":
            total,

        "employees":
            employee_names,

        "records":
            records,

        "statistics": {

            "total":
                total,

            "present":
                present,

            "absent":
                absent,

            "leave":
                leave,

            "late":
                late,

            "attendance_percentage":
                attendance_percentage,

            "department_summary":
                dept_summary
        }

    }