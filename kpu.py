import streamlit as st
import pandas as pd
import os

# --- Konstantne ---
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "kadm1n"
CSV_FILE = "db.csv"
PREDMETI = [
    "Dokazivanje u krivičnom postupku",
    "Metode obaveštajnog rada kriminalističke policije",
    "Kriminalistička taktika vođenja razgovora i ispitivanja",
    "Kriminalističke istrage nasilničkog kriminala",
    "Kriminalističke istrage visokotehnološkog kriminala"
]

# --- Funkcija za login ---
def login():
    st.title("Beleske - Login")
    username = st.text_input("Korisničko ime")
    password = st.text_input("Šifra", type="password")
    if st.button("Prijavi se"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state['logged_in'] = True
        else:
            st.error("Pogrešno korisničko ime ili šifra!")

# --- Inicijalizacija CSV-a ---
def init_csv():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=["predmet","naslov","tekst"])
        df.to_csv(CSV_FILE, index=False)

# --- Učitavanje i čuvanje CSV-a ---
def load_data():
    init_csv()
    return pd.read_csv(CSV_FILE)

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# --- Unos beleške sa momentalnim resetovanjem polja ---
def add_note(predmet):
    st.subheader(f"Unos beleške - {predmet}")
    
    # Session_state ključevi po predmetu
    naslov_key = f'naslov_{predmet}'
    tekst_key = f'tekst_{predmet}'

    if naslov_key not in st.session_state:
        st.session_state[naslov_key] = ""
    if tekst_key not in st.session_state:
        st.session_state[tekst_key] = ""
    
    # Dugme za upis beleške
    if st.button("Upiši belešku", key=f"add_button_{predmet}"):
        if st.session_state[naslov_key] and st.session_state[tekst_key]:
            df = load_data()
            df = pd.concat([df, pd.DataFrame({
                "predmet":[predmet],
                "naslov":[st.session_state[naslov_key]],
                "tekst":[st.session_state[tekst_key]]
            })], ignore_index=True)
            save_data(df)
            st.success("Beleška upisana!")

            # ODMAH reset polja
            st.session_state[naslov_key] = ""
            st.session_state[tekst_key] = ""
        else:
            st.warning("Popuni naslov i tekst!")

    # Render input polja sa vrednostima iz session_state
    st.text_input("Naslov", value=st.session_state[naslov_key], key=naslov_key)
    st.text_area("Tekst", value=st.session_state[tekst_key], key=tekst_key)

# --- Edit beleške ---
def edit_note(predmet):
    st.subheader(f"Edit beleške - {predmet}")
    df = load_data()
    df_predmet = df[df["predmet"] == predmet]
    if df_predmet.empty:
        st.info("Nema beležaka za uređivanje")
        return
    
    naslov_odabir = st.selectbox(
        "Izaberi belešku za edit",
        df_predmet["naslov"],
        key=f"edit_select_{predmet}"
    )
    
    tekst = st.text_area(
        "Tekst",
        df_predmet[df_predmet["naslov"]==naslov_odabir]["tekst"].values[0],
        key=f"edit_text_{predmet}_{naslov_odabir}"
    )
    
    if st.button("Sačuvaj izmene", key=f"save_edit_{predmet}_{naslov_odabir}"):
        df.loc[(df["predmet"]==predmet) & (df["naslov"]==naslov_odabir), "tekst"] = tekst
        save_data(df)
        st.success("Beleška je izmenjena!")

# --- Brisanje beleške ---
def delete_note(predmet):
    st.subheader(f"Brisanje beleške - {predmet}")
    df = load_data()
    df_predmet = df[df["predmet"] == predmet]
    if df_predmet.empty:
        st.info("Nema beležaka za brisanje")
        return
    naslov_odabir = st.selectbox(
        "Izaberi belešku za brisanje",
        df_predmet["naslov"],
        key=f"delete_select_{predmet}"
    )
    if st.button("Obriši", key=f"delete_button_{predmet}_{naslov_odabir}"):
        df = df[~((df["predmet"]==predmet) & (df["naslov"]==naslov_odabir))]
        save_data(df)
        st.success("Beleška obrisana!")

# --- Pregled beleški sa drop-down i pretragom ---
def view_notes(predmet):
    st.subheader(f"Pregled beleški - {predmet}")
    df = load_data()
    df_predmet = df[df["predmet"]==predmet]
    
    if df_predmet.empty:
        st.info("Nema beležaka za pregled")
        return
    
    keyword = st.text_input("Pretraži beleške po ključnoj reči", key=f"search_{predmet}")
    if keyword:
        df_predmet = df_predmet[df_predmet["naslov"].str.contains(keyword, case=False, na=False) |
                                df_predmet["tekst"].str.contains(keyword, case=False, na=False)]
        if df_predmet.empty:
            st.warning("Nema rezultata za ovu ključnu reč")
            return

    izbor = st.selectbox(
        "Izaberi belešku za pregled (ili 'Sve')",
        ["Sve"] + df_predmet["naslov"].tolist(),
        key=f"view_select_{predmet}"
    )
    
    if izbor == "Sve":
        for i, row in df_predmet.iterrows():
            st.markdown(f"**{row['naslov']}**")
            st.markdown(f"{row['tekst']}")
            st.markdown("---")
    else:
        row = df_predmet[df_predmet["naslov"]==izbor].iloc[0]
        st.markdown(f"**{row['naslov']}**")
        st.markdown(f"{row['tekst']}")

# --- Glavni ekran predmeta ---
def subject_screen(predmet):
    st.title(f"Beleske - {predmet}")
    tab = st.tabs(["Unos", "Edit", "Brisanje", "Pregled"])
    with tab[0]:
        add_note(predmet)
    with tab[1]:
        edit_note(predmet)
    with tab[2]:
        delete_note(predmet)
    with tab[3]:
        view_notes(predmet)

# --- Glavni ekran ---
def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        login()
    else:
        st.title("Beleske")
        st.subheader("Izaberi predmet")
        predmet_odabir = st.selectbox("Predmeti", PREDMETI, key="main_subject_select")
        subject_screen(predmet_odabir)

# --- Pokretanje ---
if __name__ == "__main__":
    main()
