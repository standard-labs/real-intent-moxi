import streamlit as st
import pandas as pd

# MoxiWorks Contact Import template: exactly 18 columns in this order
MOXIWORKS_TEMPLATE_COLUMNS = [
    "First Name",
    "Middle Name",
    "Last Name",
    "Company",
    "Home Street",
    "Home City",
    "Home State",
    "Home Postal Code",
    "Home Country/Region",
    "Home Phone",
    "Mobile Phone",
    "Mobile Phone 2",
    "Anniversary",
    "Birthday",
    "Categories",
    "E-mail Address",
    "E-mail 2 Address",
    "Notes",
]

# Real Intent column -> MoxiWorks column (only columns we map from; others stay empty)
REAL_INTENT_TO_MOXIWORKS = {
    "first_name": "First Name",
    "last_name": "Last Name",
    "address": "Home Street",
    "city": "Home City",
    "state": "Home State",
    "zip_code": "Home Postal Code",
    "phone_1": "Mobile Phone",
    "phone_2": "Mobile Phone 2",
    "email_1": "E-mail Address",
    "email_2": "E-mail 2 Address",
    "insight": "Notes",
}

REQUIRED_COLUMNS = ["first_name", "last_name"]


def format_phone_number(phone_value):
    """Format 10-digit numbers as ###-###-####; otherwise return string as-is."""
    if pd.isna(phone_value):
        return ""
    s = str(phone_value).strip()
    digits = "".join(c for c in s if c.isdigit())
    if len(digits) == 10:
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    return s if s else ""


def main():
    st.title("Real Intent to MoxiWorks Converter")

    st.info(
        "Upload a Real Intent CSV. The output is ready for **People → My People → gear → Import Outlook CSV** in MoxiEngage (max 2,500 contacts per file)."
    )

    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

    categories_label = st.text_input(
        "Custom label (optional)",
        placeholder="e.g. realintent or zip-90210",
        help="Enter a tag to add to the Categories column. Groups are assigned after import via My People → Add To → Groups.",
    )

    if uploaded_file is None:
        return

    df = pd.read_csv(uploaded_file)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        st.error(f"The uploaded file is missing required columns: {', '.join(missing)}.")
        return

    # Build output: only use input columns that exist
    input_cols = [c for c in REAL_INTENT_TO_MOXIWORKS if c in df.columns]
    if not input_cols:
        st.error("No mappable columns found in the uploaded CSV.")
        return

    rows = []
    for _, row in df.iterrows():
        out = {col: "" for col in MOXIWORKS_TEMPLATE_COLUMNS}
        out["Home Country/Region"] = "USA"
        if categories_label:
            out["Categories"] = categories_label.strip()

        for ri_col, moxi_col in REAL_INTENT_TO_MOXIWORKS.items():
            if ri_col not in row.index:
                continue
            val = row[ri_col]
            if pd.isna(val):
                val = ""
            else:
                val = str(val).strip()
            out[moxi_col] = val

        # Format phones
        for phone_col in ("Mobile Phone", "Mobile Phone 2"):
            out[phone_col] = format_phone_number(out[phone_col])
        # Home Phone: leave empty per template mapping

        rows.append(out)

    result = pd.DataFrame(rows)
    result = result[MOXIWORKS_TEMPLATE_COLUMNS]

    st.write("Converted data (preview):")
    st.dataframe(result)

    csv_bytes = result.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download converted CSV",
        data=csv_bytes,
        file_name="moxiworks_import.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
