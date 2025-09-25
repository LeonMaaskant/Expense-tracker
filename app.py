from flask import Flask, request
import pandas as pd
import numpy as np
from werkzeug.utils import secure_filename
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
app.config["MAX-CONTENT-LENGTH"] = 16 * 1024 * 1024

@app.route("/")
def hello_world():
    return """
        <h1>Welcome to your expense tracker!</h1>\n 
        <p> Upload your bank statement to get started.</p>
        
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="bankutskrift_fil" accept=".txt, .csv" required>
            <button type="submit">Submit</button>
        </form>
    """

@app.route("/upload", methods=["POST"])
def handle_filesubmit():
    # File validation
    if "bankutskrift_fil" not in request.files:
        return "<h2>Error: Ingen fil opplastet.</h2><a href='/'> Prøv på ny </a>"
    
    file = request.files["bankutskrift_fil"]
    
    if file.filename == "":
        return "<h2>Error: Ingen fil opplastet.</h2><a href='/'> Prøv på ny </a>"
    
    allowed_extensions = {".csv", ".txt"}
    file.ext = os.path.splitext(file.filename)[1].lower()
    if file.ext not in allowed_extensions:
        return "<h2>Error: Kun CSV og TXT filer tillatt.</h2><a href='/'> Prøv på ny </a>"
    
    safe_filename = secure_filename(file.filename)
    
    
    # Read and process the bank statement
    file.save(safe_filename)
    df = pd.read_csv(safe_filename, sep=";")
    
    # Get rid of NaN features
    df["Inn på konto"] = df["Inn på konto"].fillna(0)
    df["Ut fra konto"] = df["Ut fra konto"].fillna(0)
    
    # Calculate financial metrics
    total_in = df["Inn på konto"].sum()
    total_out = df["Ut fra konto"].sum()
    
    net_income = total_in - total_out
    
    total_transactions_incoming = (df["Inn på konto"] > 0).sum()
    total_transactions_outgoing = (df["Ut fra konto"] > 0).sum()
    
    average_transaction_size = total_out / total_transactions_outgoing
    
    
    # Biggest expense
    biggest_single_expense = df['Ut fra konto'].max()
    max_expense_index = df["Ut fra konto"].idxmax()
    max_expense_description = df.loc[max_expense_index, "Forklaring"]
    
    # Top 5 expenses
    top5_expenses_df = df[df["Ut fra konto"] != 0].sort_values(by=["Ut fra konto"]).tail(5)
    
    top5_html = top5_expenses_df[["Dato", "Forklaring", "Ut fra konto"]].to_html(
        index=False,
        classes="Table"
    )
    
    # Convert "Dato" column to datetime for analysis
    df["Dato"] = pd.to_datetime(df["Dato"], format="%d.%m.%Y")
    
    start_date = df["Dato"].min()
    end_date = df["Dato"].max()
    date_range_days = (end_date - start_date).days
    daily_spending_avg = total_out / (date_range_days + 1) if date_range_days > 0 else "Minus antall dager. FEIL."
    

    # Add category to entire dataframe
    df["Kategori"] = "annet" # default
    
    #Categorize expenses with AI
    expense_mask = df["Ut fra konto"] > 0
    expense_description = df.loc[expense_mask, "Forklaring"].tolist()
    expense_categories = categorize_with_ai(expense_description)
    df.loc[expense_mask, "Kategori"] = expense_categories
    
    # Simple categorization for income ( no need for AI since it's very simple -> cheaper without AI)
    income_mask = df["Inn på konto"] > 0
    df.loc[income_mask & df["Forklaring"].str.contains("Lønn|lonn", case=False, na=False ), "Kategori"] = "inntekt_lønn"
    df.loc[income_mask & df["Forklaring"].str.contains("Øverforing|Overforing", case=False, na=False ), "Kategori"] = "inntekt_overføring"
    
    groceries_only = df[df['Kategori'] == 'mat_dagligvare']
    grocery_html = groceries_only[["Dato", "Forklaring", "Ut fra konto"]].to_html(index=False, classes="Table")

    transport_only = df[df['Kategori'] == 'transport']  
    transport_html = transport_only[["Dato", "Forklaring", "Ut fra konto"]].to_html(index=False, classes="Table")

    shopping_only = df[df['Kategori'] == 'shopping_fritid']
    shopping_html = shopping_only[["Dato", "Forklaring", "Ut fra konto"]].to_html(index=False, classes="Table")

    lønn_only = df[df["Kategori"] == "inntekt_lønn"]
    lønn_html = lønn_only[["Dato", "Forklaring", "Inn på konto"]].to_html(index=False, classes="Table")

    overføring_only = df[df["Kategori"] == "inntekt_overføring"]
    overføring_html = overføring_only[["Dato", "Forklaring", "Inn på konto"]].to_html(index=False, classes="Table")

    # remove the bank statement for safety purposes
    os.remove(safe_filename)


    return f"""
        <p> Total penger denne måneden (inn - ut): {net_income:,.2f}. Du brukte altså {total_out:,.2f} og fikk {total_in:,.2f} inn.\n
        <p> Du hadde totalt {total_transactions_outgoing} utgående transaksjoner og {total_transactions_incoming} innkommende. </p> \n
        <p> Du brukte i gjennomsnitt {average_transaction_size:,.2f} på dine utgående kostnader. </p> \n
        <p> Din største kostnad var: {biggest_single_expense:,.2f} og kom fra: {max_expense_description} </p>
        <p> Denne starter på {start_date.strftime("%d.%m.%Y")} og slutter på {end_date.strftime("%d.%m.%Y")}. Totalt {date_range_days} dager. </p>
        <p> Du brukte i gjennomsnitt {daily_spending_avg:,.2f} per dag.</p>
        <p> Top 5 utgående med forklaring: {top5_html} </p>
        <p> Kun dagligvare: {grocery_html}</p>
        <p> Kun transport: {transport_html}</p>
        <p> Kun shopping: {shopping_html}</p>
        <p> Kun lønn: {lønn_html}</p>
        <p> Kun overføring: {overføring_html}</p>
        """
    
def categorize(data):
    categories = {
        "dagligvare": {
          "kiwi", "rema 1000", "bunnpris", "coop extra", "coop obs", "coop prix", 
          "joker", "coop marked", "coop mega", "gigaboks", "meny", "matkroken", "spar",
          "e-varekjøp"
        },
        "lonn": {"lønn", "lonn"},
        "transport": {
          "skyss", "kolumbus", "taxi", "uber", "sas airline", "nor-way", 
          "bergen trafikk", "statens vegvesen", "bussekspress"
        },
        "investering": {
          "skilling", "nordnet", "krypto", "binance"
        }

    }

    categorized = {
       "dagligvare": [],
       "lonn": [],
       "transport": [],
       "investering": [],
       "annet": []
    }

    for index, row in enumerate(data["Forklaring"]):
        row_lower = row.lower()
        category_found = False

        for category_name, keywords in categories.items():
            if any(keyword in row_lower for keyword in keywords):
                categorized[category_name].append(index)
                category_found = True
                break
            
        if not category_found:
            categorized["annet"].append(index)
    return categorized

def categorize_with_ai(transactions):
    prompt = f"""Categorize these Norwegian bank transactions into ONE of these categories: Utgifter:
                - mat_dagligvare
                - bolig
                - transport
                - helse_velvære
                - shopping_fritid
                - abonnementer
                - barn_familie
                - gaver_sosialt
                - finans
                - annet

                Transactions:
                {chr(10).join([f"{i}: {t}" for i, t in enumerate(transactions)])}

                Return ONLY a Python list of categories in the same order, like:
                ["mat_dagligvare", "bolig", "transport", ...]
                """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini", # Cheaper and faster for this task
        messages=[
            {"role": "system", "content": "You are a financial categorizer. Return only the requested format."},
            {"role": "user", "content": prompt}
        ],
        temperature=0 # makes responses more consistent
    )

    # Extract the response
    categories_str = response.choices[0].message.content.strip()

    # Convert string response to actual python list
    import ast
    categories = ast.literal_eval(categories_str)

    return categories


if __name__ == "__main__":
    app.run(debug=True)