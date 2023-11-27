

from flask import Flask, render_template, request, redirect, url_for
import sqlite3

conn = sqlite3.connect('decks2.db')

app = Flask(__name__)

class Utilisateur:
    def __init__(self, nom, email, motDePasse):
        self.nom = nom
        self.email = email
        self.motDePasse = motDePasse
        self.decks = []

    def creerDeck(self, nom, couleurs, leader, cartes, conn):
        deck = Deck(nom, couleurs, leader)
        for carte in cartes:
            deck.ajouterCarte(carte)
        self.decks.append(deck)
        deck.sauvegarder(conn)  # Sauvegarde le deck dans la base de données
        return deck

    def supprimerDeck(self, deck, conn):
        if deck in self.decks:
            self.decks.remove(deck)
            with conn:
                conn.execute("""
                    DELETE FROM cartes_decks WHERE id_deck = ?;
                """, (deck.id,))  # Assurez-vous d'avoir l'ID du deck
                conn.execute("""
                    DELETE FROM decks WHERE id = ?;
                """, (deck.id,))

    def afficherDecks(self):
        return '\n'.join([deck.afficher() for deck in self.decks])

class Carte:
    def __init__(self, nom, couleur, cout, puissance, attributs, extension, niveauCounter):
        self.nom = nom
        self.couleur = couleur
        self.cout = cout
        self.puissance = puissance
        self.attributs = attributs
        self.extension = extension
        self.niveauCounter = niveauCounter

    def sauvegarder(self, conn):
        with conn:
            cur = conn.cursor()  # Utilisation d'un curseur
            cur.execute("""
                INSERT INTO cartes (nom, couleur, cout, puissance, attributs, extension, niveau_counter)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (self.nom, self.couleur, self.cout, self.puissance, ','.join(self.attributs), self.extension, self.niveauCounter))
            self.id = cur.lastrowid
            return cur.lastrowid  # Retourne l'ID de la carte insérée avec le curseur

class Leader(Carte):
    def __init__(self, nom, couleur, cout, puissance, attributs, extension, niveauCounter, pouvoirSpecial):
        super().__init__(nom, couleur, cout, puissance, attributs, extension, niveauCounter)
        self.pouvoirSpecial = pouvoirSpecial

class Deck:
    def __init__(self, nom, couleurs, leader):
        self.id = None  # Ajout de l'attribut id
        self.nom = nom
        self.couleurs = couleurs
        self.leader = leader
        self.cartes = []
    
    def ajouterCarte(self, carte):
        self.cartes.append(carte)

    def sauvegarder(self, conn):
        with conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO decks (nom, couleurs, leader)
                VALUES (?, ?, ?);
            """, (self.nom, ','.join(self.couleurs), self.leader.nom))
            self.id = cur.lastrowid  # Mise à jour de l'id après l'insertion

            for carte in self.cartes:
                id_carte = carte.sauvegarder(conn)
                cur.execute("""
                    INSERT INTO cartes_decks (id_carte, id_deck)
                    VALUES (?, ?);
                """, (id_carte, self.id))

    def supprimerCarte(self, carte, conn):
        if carte in self.cartes:
            self.cartes.remove(carte)
            with conn:
                conn.execute("""
                    DELETE FROM cartes_decks WHERE id_carte = ? AND id_deck = ?;
                """, (carte.id, self.id))
                
def creer_tables():
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cartes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT,
                couleur TEXT,
                cout INTEGER,
                puissance INTEGER,
                attributs TEXT,
                extension TEXT,
                niveau_counter INTEGER
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS decks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT,
                couleurs TEXT,
                leader TEXT
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cartes_decks (
                id_carte INTEGER,
                id_deck INTEGER,
                FOREIGN KEY (id_carte) REFERENCES cartes (id),
                FOREIGN KEY (id_deck) REFERENCES decks (id)
            );
        """)
        
        
def afficher_table(conn, nom_table):
    print(f"Contenu de la table {nom_table}:")
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {nom_table}")
    rows = cur.fetchall()
    for row in rows:
        print(row)
    print("\n")
    
creer_tables()

# Création et sauvegarde des cartes et du leader
carte_luffy = Carte("Luffy", "Rouge", 5, 7000, ["Equipage du chapeau de paille", "Supernovas"], "OP-01", 1000)
carte_ace = Carte("Ace", "Rouge", 7, 9000, ["Equipage de Barbe blanche"], "OP-02", 2000)

leader_whitebeard = Leader("Edward Newgate", "Rouge", 5, 6000, ["Equipage de Barbe blanche", "Commandement"], "OP-03", 0, "Pioche une carte des points de vies")

# Création et sauvegarde du deck
deck_whitebeard = Deck("Deck_whitebeard", ["Rouge"], leader_whitebeard)
deck_whitebeard.ajouterCarte(carte_luffy)
deck_whitebeard.ajouterCarte(carte_ace)
deck_whitebeard.sauvegarder(conn)

afficher_table(conn, "cartes")
afficher_table(conn, "decks")
afficher_table(conn, "cartes_decks")

utilisateur = Utilisateur("Nico", "test@nicolas.com", "test")
utilisateur.decks.append(deck_whitebeard)


# Utility functions to interact with the database
def get_db_connection():
    conn = sqlite3.connect('decks2.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_decks():
    conn = get_db_connection()
    decks = conn.execute('SELECT * FROM decks').fetchall()
    conn.close()
    return decks

def add_deck(deck_name, colors, leader_name):
    conn = get_db_connection()
    # Add more logic if needed for inserting into decks
    conn.execute('INSERT INTO decks (nom, couleurs, leader) VALUES (?, ?, ?)',
                 (deck_name, colors, leader_name))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return redirect(url_for('show_decks'))

@app.route('/decks')
def show_decks():
    decks = get_decks()
    return render_template('decks.html', decks=decks)

@app.route('/add_deck', methods=['GET', 'POST'])
def add_deck_route():
    if request.method == 'POST':
        deck_name = request.form['deck_name']
        colors = request.form['colors']  # Assuming colors are provided as a comma-separated string
        leader_name = request.form['leader_name']
        add_deck(deck_name, colors, leader_name)
        return redirect(url_for('show_decks'))
    return render_template('add_deck.html')

if __name__ == '__main__':
    app.run(debug=True)
