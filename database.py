# database.py
import sqlite3

def get_db_connection():
    conn = sqlite3.connect('bdd_cartes.db')
    conn.row_factory = sqlite3.Row
    return conn



def creer_tables():
    conn = get_db_connection()
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
                niveau_counter INTEGER,
                image_path TEXT
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS decks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT,
                couleurs TEXT,
                leader TEXT,
                user_id INTEGER,
                leader_id INTEGER,
                FOREIGN KEY (leader_id) REFERENCES leaders(id)
                FOREIGN KEY (user_id) REFERENCES utilisateurs(id)
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
        conn.execute('''
            CREATE TABLE IF NOT EXISTS leaders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT,
                couleur TEXT,
                puissance INTEGER,
                effet TEXT,
                attributs TEXT,
                points_de_vie INTEGER,
                reference TEXT,
                image_path TEXT
            );
        ''')

        
def afficher_table(conn, nom_table):
    print(f"Contenu de la table {nom_table}:")
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {nom_table}")
    rows = cur.fetchall()
    for row in rows:
        print(row)
    print("\n")
    

def get_decks(user_id):
    conn = get_db_connection()
    decks = conn.execute('SELECT * FROM decks').fetchall()
    conn.close()
    return decks

    
def add_deck(user_id, deck_name, colors, leader_id):
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO decks (user_id, nom, couleurs, leader_id) VALUES (?, ?, ?, ?)
    ''', (user_id, deck_name, colors, leader_id))
    conn.commit()
    conn.close()

#def ajouter_user_id_aux_decks():
 #   conn = sqlite3.connect('bdd.db')
  #  with conn:
   #     conn.execute("ALTER TABLE decks ADD COLUMN user_id INTEGER;")
    #conn.close()


def get_user_db_connection():
    conn = sqlite3.connect('userdb.db')
    conn.row_factory = sqlite3.Row
    return conn


def creer_table_utilisateurs():
    conn = get_user_db_connection()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS utilisateurs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT,
                email TEXT UNIQUE,
                motDePasse TEXT
            );
        """)
    conn.close()

def ajouter_carte_au_deck(deck_id, carte_id):
    conn = get_db_connection()
    conn.execute('INSERT INTO cartes_decks (id_carte, id_deck) VALUES (?, ?)', (carte_id, deck_id))
    conn.commit()
    conn.close()


def get_all_cartes():
    conn = get_db_connection()
    cartes = conn.execute('SELECT * FROM cartes').fetchall()
    # Convertir chaque row en dictionnaire pour permettre la modification
    cartes_liste = [dict(carte) for carte in cartes]
    for carte in cartes_liste:
        carte['image_path'] = carte['image_path'].replace('\\', '/')
    conn.close()
    return cartes_liste


def get_cartes_from_deck(deck_id):
    conn = get_db_connection()
    cartes = conn.execute('''
        SELECT c.* FROM cartes c
        INNER JOIN cartes_decks cd ON c.id = cd.id_carte
        WHERE cd.id_deck = ?
    ''', (deck_id,)).fetchall()
    cartes_list = [dict(carte) for carte in cartes]
    for carte in cartes_list:
        # Assurez-vous que image_path utilise des slashes (/) au lieu de backslashes (\)
        if carte['image_path']:
            carte['image_path'] = carte['image_path'].replace('\\', '/')
    conn.close()
    return cartes_list

def ajouter_carte(nom, couleur, cout, puissance, attributs, extension, niveau_counter, image_path):
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO cartes (nom, couleur, cout, puissance, attributs, extension, niveau_counter, image_path) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (nom, couleur, cout, puissance, attributs, extension, niveau_counter, image_path))
    conn.commit()
    conn.close()

def ajouter_leader(nom, couleur, puissance, effet, attributs, points_de_vie, reference, image_path):
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO leaders (nom, couleur, puissance, effet, attributs, points_de_vie, reference, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (nom, couleur, puissance, effet, attributs, points_de_vie, reference, image_path))
    conn.commit()
    conn.close()


def ajouter_leader_id_aux_decks():
    conn = get_db_connection()
    with conn:
        conn.execute('ALTER TABLE decks ADD COLUMN leader_id INTEGER REFERENCES leaders(id)')
    conn.close()

def get_all_leaders():
    conn = get_db_connection()
    leaders = conn.execute('SELECT * FROM leaders').fetchall()
    conn.close()
    return leaders

def get_leader_from_deck(deck_id):
    conn = get_db_connection()
    leader = conn.execute('''
        SELECT l.* FROM leaders l
        JOIN decks d ON l.id = d.leader_id
        WHERE d.id = ?
    ''', (deck_id,)).fetchone()
    conn.close()

    if leader:
        leader_dict = dict(leader)
        if leader_dict['image_path']:
            leader_dict['image_path'] = leader_dict['image_path'].replace('\\', '/')
        return leader_dict
    return None

def supprimer_carte_de_deck(deck_id, carte_id):
    conn = get_db_connection()
    conn.execute('''
        DELETE FROM cartes_decks WHERE id_deck = ? AND id_carte = ?
    ''', (deck_id, carte_id))
    conn.commit()
    conn.close()

def get_deck_details(deck_id):
    conn = get_db_connection()
    deck = conn.execute('SELECT * FROM decks WHERE id = ?', (deck_id,)).fetchone()
    leader = None
    if deck and deck['leader_id']:
        leader = get_leader_from_deck(deck['leader_id'])
    cartes = get_cartes_from_deck(deck_id)
    conn.close()
    return deck, leader, cartes
