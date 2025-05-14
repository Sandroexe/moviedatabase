from mysql.connector import connect, Error
import tkinter as tk
from tkinter import simpledialog, ttk, messagebox
import subprocess
import time
import psutil
import os


def find_xampp_installation():
    # Laufwerke nach XAMPP-Installation durchsuchen
    for laufwerk in ['C:', 'D:', 'E:', 'F:', 'G:']:
        xampp_pfad = os.path.join(laufwerk, '\XAMPP')
        if os.path.isdir(xampp_pfad):
            return xampp_pfad



def is_mysql_running():
    # Prüfen, ob MySQL bereits läuft
    for proc in psutil.process_iter(attrs=['name']):
        if 'mysqld' in proc.info['name'].lower():
            return True
    return False


def start_mysql(xampp_pfad):
    mysqld_exe = os.path.join(xampp_pfad, 'mysql', 'bin', 'mysqld.exe')
    my_ini = os.path.join(xampp_pfad, 'mysql', 'bin', 'my.ini')
    try:
        print(f"Starte MySQL von: {mysqld_exe}")
        subprocess.Popen([mysqld_exe, f"--defaults-file={my_ini}"], shell=True)
        print("MySQL-Server wird gestartet...")
    except Exception as e:
        print(f"ERROR: Fehler beim Start von MySQL: {e}")
        if e.errno:
            print(f"Fehlercode: {e.errno}")


def connect_db():
    # Suche nach einer gültigen XAMPP-Installation und starte MySQL, falls nicht bereits aktiv
    print("Suche nach XAMPP-Installation...")
    xampp_pfad = find_xampp_installation()

    if xampp_pfad is None:
        print("ERROR: Keine gültige XAMPP-Installation gefunden.")
        return None

    print(f"XAMPP gefunden unter: {xampp_pfad}")

    # MySQL nur starten, wenn es nicht schon läuft
    if not is_mysql_running():
        start_mysql(xampp_pfad)
    else:
        print("MySQL läuft bereits.")

    # GUI-Dialog für Benutzername und Passwort
    root = tk.Tk()
    root.withdraw()  # Kein Hauptfenster anzeigen
    user = simpledialog.askstring("Login", "Benutzername:")
    password = simpledialog.askstring("Login", "Passwort:", show="*")
    root.destroy()

    # kurz Warten und dann 5 Mal versuchen Verbindung aufzubauen
    for i in range(5):
        try:
            connection = connect(
                host="localhost",
                user=user,
                password=password,
            )
            print("Verbindung erfolgreich.")
            return connection
        except Error as e:
            print(f"Verbindungsversuch {i+1} fehlgeschlagen...")
            time.sleep(1)

    print("Fehler: Verbindung zu MySQL nicht möglich.")
    return None



def create_database_tables_and_insert_data(conn):
    try:
        
        if conn is None:
            return
        cursor = conn.cursor()

        #Datenbank erstellen
        create_db_query = "create database if not exists movie_database"
        cursor.execute(create_db_query)

        print(f"Datenbank movie_database erstellt oder vorhanden")
        
        #Datenbank auswählen
        cursor.execute("USE movie_database")

        # Tabellen erstellen
        table_definitions = {
            "movies": """
                CREATE TABLE IF NOT EXISTS movies (
                    movie_id INT(11) PRIMARY KEY,
                    title VARCHAR(100),
                    release_year YEAR,
                    genre VARCHAR(100),
                    collection_in_mil DECIMAL(6,1)
                );
            """,
            "reviewers": """
                CREATE TABLE IF NOT EXISTS reviewers (
                    reviewer_id INT(11) PRIMARY KEY,
                    name VARCHAR(100),
                    surname VARCHAR(100)
                );
            """,
            "ratings": """
                CREATE TABLE IF NOT EXISTS ratings (
                    movie_id_fk INT(11),
                    reviewer_id_fk INT(11),
                    rating DECIMAL(2,1),
                    FOREIGN KEY (movie_id_fk) REFERENCES movies(movie_id)
                        ON DELETE CASCADE ON UPDATE CASCADE,
                    FOREIGN KEY (reviewer_id_fk) REFERENCES reviewers(reviewer_id)
                        ON DELETE CASCADE ON UPDATE CASCADE
                );
            """
        }

        for name, sql in table_definitions.items():
            cursor.execute(sql)
            print(f"Tabelle erstellt oder vorhanden: {name}")

        # Daten einfügen
        data_definitions = {
            "movies": {
                "data": [
                    (1, 'The Shawshank Redemption', 1994, 'Drama', 28.4),
                    (2, 'The Godfather', 1972, 'Crime', 134.9),
                    (3, 'The Dark Knight', 2008, 'Action', 1005.0),
                    (4, '12 Angry Men', 1957, 'Drama', 4.4),
                    (5, 'Schindlers List', 1993, 'History', 322.2),
                    (6, 'Pulp Fiction', 1994, 'Crime', 213.9),
                    (7, 'The Lord of the Rings: The Return of the King', 2003, 'Fantasy', 1142.0),
                    (8, 'Fight Club', 1999, 'Drama', 100.9),
                    (9, 'Inception', 2010, 'Sci-Fi', 829.9),
                    (10, 'Forrest Gump', 1994, 'Romance', 678.2),
                    (11, 'The Matrix', 1999, 'Sci-Fi', 466.3),
                    (12, 'Goodfellas', 1990, 'Crime', 47.1),
                    (13, 'Se7en', 1995, 'Thriller', 327.3),
                    (14, 'Gladiator', 2000, 'Action', 460.5),
                    (15, 'The Silence of the Lambs', 1991, 'Thriller', 272.7),
                    (16, 'The Green Mile', 1999, 'Drama', 286.8),
                    (17, 'Interstellar', 2014, 'Sci-Fi', 701.7),
                    (18, 'Saving Private Ryan', 1998, 'War', 482.3),
                    (19, 'The Prestige', 2006, 'Mystery', 109.7),
                    (20, 'The Lion King', 1994, 'Animation', 968.5),
                    (21, 'Whiplash', 2014, 'Drama', 49.0),
                    (22, 'The Departed', 2006, 'Crime', 291.5),
                    (23, 'The Pianist', 2002, 'Biography', 120.1),
                    (24, 'Django Unchained', 2012, 'Western', 425.4),
                    (25, 'Avengers: Endgame', 2019, 'Action', 2797.5),
                    (26, 'Parasite', 2019, 'Thriller', 258.8),
                    (27, 'Joker', 2019, 'Drama', 1074.3),
                    (28, 'The Wolf of Wall Street', 2013, 'Biography', 392.0),
                    (29, 'Coco', 2017, 'Animation', 807.1),
                    (30, 'Toy Story', 1995, 'Animation', 373.6)
                ],
                "query": """
                    INSERT INTO movies 
                    (movie_id, title, release_year, genre, collection_in_mil) 
                    VALUES (%s, %s, %s, %s, %s)
                """
            },
            "ratings": {
                "data": [
                    (1, 1, 9.5),
                    (2, 2, 9.2),
                    (3, 3, 9.0),
                    (4, 4, 8.5),
                    (5, 1, 8.9),
                    (6, 2, 8.7),
                    (7, 3, 8.0),
                    (8, 4, 9.1),
                    (9, 5, 9.0),
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

        # Tabellen leeren und befüllen
        for table, content in data_definitions.items():
            cursor.execute(f"DELETE FROM {table}")
            connection.commit()

            cursor.executemany(content["query"], content["data"])
            connection.commit()
            print(f"{len(content['data'])} Einträge in '{table}' eingefügt.")

    except Error as e:
        print(f"Fehler: {e}")

    except KeyboardInterrupt:
        print("\nVon Benutzer abgebrochen.")


def search_movies_by_year(cursor, year):
    cursor.execute("SELECT title, genre, collection_in_mil FROM movies WHERE release_year = %s", (year,))
    results = cursor.fetchall()
    if results:
        return "\n".join([f"• {title} ({genre}, {revenue} Mio. $)" for title, genre, revenue in results]) + "\n"
    else:
        return "Keine Filme gefunden.\n"


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
        return "\n".join([f"- {reviewer} bewertete '{title}' mit {rating}/10⭐" for rating, reviewer in results]) + "\n"
    else:
        return "Keine Bewertungen gefunden.\n"



def show_reviews_by_reviewer(cursor, name):
    cursor.execute("""
        SELECT m.title, r.rating
        FROM ratings r
        JOIN movies m ON r.movie_id_fk = m.movie_id
        JOIN reviewers v ON r.reviewer_id_fk = v.reviewer_id
        WHERE v.name = %s OR v.surname = %s
    """, (name,name,))
    results = cursor.fetchall()
    if results:
        return "\n".join([f"- {title}: {rating}/10 ⭐" for title, rating in results]) + "\n"
    else:
        return "Keine Bewertungen von diesem Benutzer gefunden.\n"


def show_average_rating(cursor, title):
    cursor.execute("""
        SELECT AVG(r.rating)
        FROM ratings r
        JOIN movies m ON r.movie_id_fk = m.movie_id
        WHERE m.title = %s
    """, (title,))
    result = cursor.fetchone() 
    if result:
        return f"Durchschnittliche Bewertung für '{title}': {round(result[0], 2)}/10 ⭐" + "\n"
    else:
        return "Keine Bewertungen vorhanden.\n"


# Haupt-GUI
def main(conn):
    
    if conn is None:
        return
    cursor = conn.cursor()

    def anzeigen_text(event=None):
        eingabe = eingabe_feld.get().strip()
        auswahl = combo.get()

        if not eingabe or auswahl == "Bitte wählen...":
            messagebox.showwarning("Fehlende Eingabe", "Bitte geben Sie etwas ein und wählen Sie ein Kriterium aus.")
            return

        if auswahl == "Erscheinungsjahr 🎬":
            ergebnis = search_movies_by_year(cursor, int(eingabe))
        elif auswahl == "Filmbewertung ⭐":
            ergebnis = show_reviews_for_movie(cursor, eingabe)
        elif auswahl == "Reviewer":
            ergebnis = show_reviews_by_reviewer(cursor, eingabe)
        elif auswahl == "Durchschnittsbewertung":
            ergebnis = show_average_rating(cursor, eingabe)
        else:
            ergebnis = "Ungültige Auswahl."

        ausgabe_feld.config(state='normal')
        ausgabe_feld.insert(tk.END, ergebnis)
        ausgabe_feld.config(state='disabled')

    def loeschen_text(event=None):
        ausgabe_feld.config(state='normal')
        ausgabe_feld.delete("1.0", tk.END)

    # Fenster erstellen
    fenster = tk.Tk()
    fenster.title("Movie Database Suche")
    fenster.geometry("700x450")
    fenster.configure(bg="#f0f0f0")

    for i in range(2):
        fenster.grid_columnconfigure(i, weight=1)  # Spalten dehnen sich mit

    # Überschrift
    header = tk.Label(fenster, text="Filmdatenbank-Suche", font=("Helvetica", 16, "bold"), bg="#f0f0f0")
    header.grid(row=0, column=0, columnspan=2, pady=10)

    # Eingabe
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

    # Suchbutton (zentriert mit eigenem Frame)
    button_frame = tk.Frame(fenster, bg="#f0f0f0")
    button_frame.grid(row=3, column=0, columnspan=1, pady=10)
    anzeigen_button = tk.Button(button_frame, text="Suchen", command=anzeigen_text, bg="#4CAF50", fg="white", padx=10, pady=5, font=("Arial Bold",12))
    anzeigen_button.pack()

    # Suchverlauf löschen
    button_frame = tk.Frame(fenster, bg="#f0f0f0")
    button_frame.grid(row=3, column=1, columnspan=1, pady=10)
    anzeigen_button = tk.Button(button_frame, text="Verlauf löschen", command=loeschen_text, bg="red", fg="white", padx=10, pady=5, font=("Arial Bold",12))
    anzeigen_button.pack()

    # Ausgabe mit Scrollbar (zentriert und anpassbar)
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


if __name__ == "__main__":
    
    #Verbindung herstellen
    connection = connect_db()

    # Datenbank erstellen und befüllen
    create_database_tables_and_insert_data(connection)
    
    # GUI starten
    main(connection)
