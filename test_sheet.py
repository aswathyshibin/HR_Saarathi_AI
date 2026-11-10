from backend.sheets_service import (
    get_attendance_dataframe,
    get_employee_names
)


print()
print("=" * 60)
print("HR SAARATHI - GOOGLE SHEET TEST")
print("=" * 60)


try:

    print("\nConnecting to Google Sheet...")

    df = get_attendance_dataframe()

    print("\nConnection successful! ✅")

    print("\nAttendance data:")

    if df.empty:

        print("No attendance records found.")

    else:

        print(
            df.to_string(
                index=False
            )
        )


    print("\nNumber of records:")

    print(len(df))


    print("\nEmployee names:")

    employees = get_employee_names()

    if employees:

        for employee in employees:

            print(
                " -",
                employee
            )

    else:

        print("No employees found.")


    print("\n" + "=" * 60)

    print(
        "GOOGLE SHEET CONNECTION WORKING"
    )

    print("=" * 60)


except Exception as e:

    print("\nERROR")

    print(
        type(e).__name__
        + ": "
        + str(e)
    )