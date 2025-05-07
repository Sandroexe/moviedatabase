# Bibliotheken importieren
from mysql.connector import connect, Error  # Für die Datenbankverbindung
import tkinter as tk  # Für die GUI
from tkinter import ttk, messagebox  # Erweiterte Widgets und Dialoge
from getpass import getpass  # Sichere Passwortabfrage über die Konsole


# Funktion zum Herstellen der Verbindung zur MySQL-Datenbank
def connect_db():
    try:
        connection = connect(
            host="localhost",
            user=input("Enter username: "),  # Benutzername eingeben
            password=getpass("Enter password: "),  # Passwort sicher eingeben
        )
        return connection
    except Error as e:
        print(f"Verbindungsfehler: {e}")
        return None
    except KeyboardInterrupt:
        print("von user abgebrochen")


# Funktion zum Erstellen der Tabellen und Einfügen von Beispieldaten
def create_database_tables_and_insert_data(conn):
    try:
        if conn is None:
            return

        cursor = conn.cursor()

        # Datenbank erstellen, falls sie nicht existiert
        create_db_query = "create database if not exists movie_database"
        cursor.execute(create_db_query)
        print(f"Datenbank movie_database erstellt oder vorhanden")

        # Datenbank auswählen
        cursor.execute("USE movie_database")

        # Tabellen-Definitionen
        table_definitions = {
            "movies": """
                CREATE TABLE IF NOT EXISTS movies (
                    movie_id INT(11),
                    title VARCHAR(100),
                    release_year YEAR,
                    genre VARCHAR(100),
                    collection_in_mil DECIMAL(4,1)
                );
            """,
            "ratings": """
                CREATE TABLE IF NOT EXISTS ratings (
                    movie_id_fk INT(11),
                    reviewer_id_fk INT(11),
                    rating DECIMAL(2,1)
                );
            """,
            "reviewers": """
                CREATE TABLE IF NOT EXISTS reviewers (
                    reviewer_id INT(11),
                    name VARCHAR(100),
                    surname VARCHAR(100)
                );
            """
        }

        # Tabellen ausführen/erstellen
        for name, sql in table_definitions.items():
            cursor.execute(sql)
            print(f"Tabelle erstellt oder vorhanden: {name}")

        # Beispiel-Daten definieren
        data_definitions = {
            "movies": {
                "data": [
                    (1, "The Shawshank Redemption", "Drama", 1994, 73.3),
                    (2, "The Godfather", "Crime", 1972, 291.0),
                    (3, "The Dark Knight", "Action", 2008, 1006.0),
                    (4, "Pulp Fiction", "Crime", 1994, 213.9),
                    (5, "Inception", "Sci-Fi", 2010, 836.8),
                    (6, "Forrest Gump", "Drama", 1994, 678.2),
                    (7, "The Matrix", "Sci-Fi", 1999, 465.3),
                    (8, "Parasite", "Thriller", 2019, 258.7),
                    (9, "Interstellar", "Sci-Fi", 2014, 701.7),
                    (10, "The Lion King", "Animation", 1994, 968.5),
                ],
                "query": """
                    INSERT INTO movies 
                    (movie_id, title, genre, release_year, collection_in_mil) 
                    VALUES (%s, %s, %s, %s, %s)
                """
            },
            "ratings": {
                "data": [
                    (1, 1, 9.5), (2, 2, 9.2), (3, 3, 9.0),
                    (4, 4, 8.5), (5, 1, 8.9), (6, 2, 8.7),
                    (7, 3, 8.0), (8, 4, 9.1), (9, 5, 9.0),
                    (10, 2, 8.6)
                ],
                "query": """
                    INSERT INTO ratings
                    (movie_id_fk, reviewer_id_fk, rating) 
                    VALUES (%s, %s, %s)
                """
            },
            "reviewers": {
                "data": [
                    (1, 'Anna', 'Schmidt'),
                    (2, 'Tom', 'Becker'),
                    (3, 'Lisa', 'Meier'),
                    (4, 'Max', 'Hoffmann'),
                    (5, 'Julia', 'Weber'),
                ],
                "query": """
                    INSERT INTO reviewers
                    (reviewer_id, name, surname) 
                    VALUES (%s, %s, %s)
                """
            }
        }

        # Bestehende Daten löschen und neue einfügen
        for table, content in data_definitions.items():
            cursor.execute(f"DELETE FROM {table}")
            connection.commit()

            cursor.executemany(content["query"], content["data"])
            connection.commit()
            print(f"{len(content['data'])} Einträge in '{table}' eingefügt.")

    except Error as e:
        print(f"Fehler: {e}")
    except KeyboardInterrupt:
        print("Von Benutzer abgebrochen.")


# Funktion: Filme nach Erscheinungsjahr suchen
def search_movies_by_year(cursor, year):
    cursor.execute("SELECT title, genre, collection_in_mil FROM movies WHERE release_year = %s", (year,))
    results = cursor.fetchall()
    if results:
        return "\n".join([f"• {title} ({genre}, {revenue} Mio. $)" for title, genre, revenue in results])
    else:
        return "Keine Filme gefunden."


# Funktion: Bewertungen zu einem bestimmten Film anzeigen
def show_reviews_for_movie(cursor, title):
    cursor.execute("""
        SELECT r.rating, v.name
        FROM ratings r
        JOIN movies m ON r.movie_id_fk = m.movie_id
        JOIN reviewers v ON r.reviewer_id_fk = v.reviewer_id
        WHERE m.title = %s
    """, (title,))
    results = cursor.fetchall()
    if results:
        return "\n".join([f"- {reviewer} bewertete '{title}' mit {rating}/10" for rating, reviewer in results])
    else:
        return "Keine Bewertungen gefunden."


# Funktion: Alle Bewertungen eines bestimmten Reviewers anzeigen
def show_reviews_by_reviewer(cursor, name):
    cursor.execute("""
        SELECT m.title, r.rating
        FROM ratings r
        JOIN movies m ON r.movie_id_fk = m.movie_id
        JOIN reviewers v ON r.reviewer_id_fk = v.reviewer_id
        WHERE v.name = %s OR v.surname = %s
    """, (name, name,))
    results = cursor.fetchall()
    if results:
        return "\n".join([f"- {title}: {rating}/10" for title, rating in results])
    else:
        return "Keine Bewertungen von diesem Benutzer gefunden."


# Funktion: Durchschnittliche Bewertung eines Films berechnen
def show_average_rating(cursor, title):
    cursor.execute("""
        SELECT AVG(r.rating)
        FROM ratings r
        JOIN movies m ON r.movie_id_fk = m.movie_id
        WHERE m.title = %s
    """, (title,))
    result = cursor.fetchone()
    if result:
        return f"Durchschnittliche Bewertung für '{title}': {round(result[0], 2)}/10"
    else:
        return "Keine Bewertungen vorhanden."


# Hauptfunktion für die GUI
def main(conn):
    if conn is None:
        return
    cursor = conn.cursor()

    # Funktion für den Button oder ENTER
    def anzeigen_text(event=None):
        eingabe = eingabe_feld.get().strip()
        auswahl = combo.get()

        if not eingabe or auswahl == "Bitte wählen...":
            messagebox.showwarning("Fehlende Eingabe", "Bitte geben Sie etwas ein und wählen Sie ein Kriterium aus.")
            return

        # Auswahl je nach Benutzeraktion auswerten
        if auswahl == "Erscheinungsjahr 🎬":
            ergebnis = search_movies_by_year(cursor, eingabe)
        elif auswahl == "Filmbewertung ⭐":
            ergebnis = show_reviews_for_movie(cursor, eingabe)
        elif auswahl == "Reviewer":
            ergebnis = show_reviews_by_reviewer(cursor, eingabe)
        elif auswahl == "Durchschnittsbewertung":
            ergebnis = show_average_rating(cursor, eingabe)
        else:
            ergebnis = "Ungültige Auswahl."

        # Ausgabe anzeigen
        ausgabe_feld.config(state='normal')
        ausgabe_feld.delete("1.0", tk.END)
        ausgabe_feld.insert(tk.END, ergebnis)
        ausgabe_feld.config(state='disabled')

    # GUI-Fenster aufbauen
    fenster = tk.Tk()
    fenster.title("Movie Database Suche")
    fenster.geometry("700x450")
    fenster.configure(bg="#f0f0f0")

    # Layout konfigurieren
    for i in range(2):
        fenster.grid_columnconfigure(i, weight=1)

    # Überschrift
    header = tk.Label(fenster, text="Filmdatenbank-Suche", font=("Helvetica", 16, "bold"), bg="#f0f0f0")
    header.grid(row=0, column=0, columnspan=2, pady=10)

    # Eingabefeld
    tk.Label(fenster, text="Eingabe:", font=("Helvetica", 11), bg="#f0f0f0").grid(row=1, column=0, sticky="e", padx=10)
    eingabe_feld = tk.Entry(fenster, width=40)
    eingabe_feld.grid(row=1, column=1, pady=5, sticky="w")
    eingabe_feld.bind("<Return>", anzeigen_text)

    # Auswahlfeld
    tk.Label(fenster, text="Suchkriterium:", font=("Helvetica", 11), bg="#f0f0f0").grid(row=2, column=0, sticky="e", padx=10)
    optionen = ["Filmbewertung ⭐", "Erscheinungsjahr 🎬", "Reviewer", "Durchschnittsbewertung"]
    combo = ttk.Combobox(fenster, values=optionen, state="readonly", width=37)
    combo.set("Bitte wählen...")
    combo.grid(row=2, column=1, pady=5, sticky="w")

    # Button
    button_frame = tk.Frame(fenster, bg="#f0f0f0")
    button_frame.grid(row=3, column=0, columnspan=2, pady=10)
    anzeigen_button = tk.Button(button_frame, text="Suchen", command=anzeigen_text, bg="#4CAF50", fg="white", padx=10, pady=5)
    anzeigen_button.pack()

    # Textausgabe mit Scrollbar
    ausgabe_frame = tk.Frame(fenster, bg="#f0f0f0")
    ausgabe_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
    fenster.grid_rowconfigure(4, weight=1)

    ausgabe_feld = tk.Text(ausgabe_frame, height=10, wrap='word', state='disabled', bg="#ffffff", font=("Courier", 10))
    scrollbar = tk.Scrollbar(ausgabe_frame, command=ausgabe_feld.yview)
    ausgabe_feld.configure(yscrollcommand=scrollbar.set)

    ausgabe_feld.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky='ns')
    ausgabe_frame.grid_columnconfigure(0, weight=1)
    ausgabe_frame.grid_rowconfigure(0, weight=1)

    fenster.mainloop()
    conn.close()


# Einstiegspunkt: Erst Verbindung, dann Datenbank, dann GUI
if __name__ == "__main__":
    connection = connect_db()
    create_database_tables_and_insert_data(connection)
    main(connection)

