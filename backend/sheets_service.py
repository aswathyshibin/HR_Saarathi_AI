import requests
import pandas as pd

from .config import (
    APPS_SCRIPT_URL,
    APPS_SCRIPT_SECRET
)


def call_apps_script(action="attendance"):

    params = {
        "token": APPS_SCRIPT_SECRET,
        "action": action
    }

    print("\n----------------------------------------")
    print("Calling Apps Script...")
    print("Action:", action)
    print("URL:", APPS_SCRIPT_URL)
    print("----------------------------------------")

    response = requests.get(
        APPS_SCRIPT_URL,
        params=params,
        timeout=30,
        allow_redirects=True
    )

    print("HTTP Status:", response.status_code)
    print("Final URL:", response.url)
    print("Content-Type:",
          response.headers.get("Content-Type"))

    print("\nResponse preview:")
    print(response.text[:500])

    response.raise_for_status()

    try:

        data = response.json()

    except ValueError:

        raise RuntimeError(
            "Apps Script did not return JSON.\n\n"
            "HTTP Status: "
            + str(response.status_code)
            + "\n\n"
            "Response:\n"
            + response.text[:1000]
        )

    if not data.get("success", False):

        raise RuntimeError(
            data.get(
                "error",
                "Apps Script returned an error."
            )
        )

    return data


def get_attendance_dataframe():

    result = call_apps_script(
        "attendance"
    )

    records = result.get(
        "data",
        []
    )

    if not records:

        return pd.DataFrame()

    df = pd.DataFrame(records)

    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    df = df.dropna(
        how="all"
    )

    return df


def get_employee_names():

    result = call_apps_script(
        "employees"
    )

    return result.get(
        "data",
        []
    )