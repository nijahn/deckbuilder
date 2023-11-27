# app.py
import os
import sqlite3
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session
from models import Utilisateur, Carte, Leader, Deck
from database import creer_tables, get_db_connection, get_decks, add_deck, afficher_table, get_user_db_connection, creer_table_utilisateurs, ajouter_carte_au_deck, get_all_cartes, get_cartes_from_deck, ajouter_carte, ajouter_leader,ajouter_leader_id_aux_decks, get_all_leaders, get_leader_from_deck, get_deck_details
creer_table_utilisateurs()

creer_tables()


conn = get_db_connection()
# Création et sauvegarde des cartes et du leader
#carte_luffy = Carte("Luffy", "Rouge", 5, 7000, ["Equipage du chapeau de paille", "Supernovas"], "OP-01", 1000)
#carte_ace = Carte("Ace", "Rouge", 7, 9000, ["Equipage de Barbe blanche"], "OP-02", 2000)

#leader_whitebeard = Leader("Edward Newgate", "Rouge", 5, 6000, ["Equipage de Barbe blanche", "Commandement"], "OP-03", 0, "Pioche une carte des points de vies")

# Création et sauvegarde du deck
#deck_whitebeard = Deck("Deck_whitebeard2", ["Rouge"], leader_whitebeard)
#deck_whitebeard.ajouterCarte(carte_luffy)
#deck_whitebeard.ajouterCarte(carte_ace)
#deck_whitebeard.sauvegarder(conn)

afficher_table(conn, "cartes")
afficher_table(conn, "decks")
afficher_table(conn, "cartes_decks")


#utilisateur = Utilisateur("Nico", "test@nicolas.com", "test")
#utilisateur.decks.append(deck_whitebeard)
conn.close()

app = Flask(__name__)
app.secret_key = '4697'
@app.route('/')
def index():
    return redirect(url_for('show_decks'))

@app.route('/decks')
def show_decks():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login'))
    decks = get_decks(user_id)
    return render_template('decks.html', decks=decks)


@app.route('/add_deck', methods=['GET', 'POST'])
def add_deck_route():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login'))

    # Récupérer la liste des leaders pour le menu déroulant
    leaders = get_all_leaders()

    if request.method == 'POST':
        deck_name = request.form['deck_name']
        colors = request.form['colors']
        leader_id = request.form['leader_id']  # Assurez-vous que ce champ est présent dans votre formulaire
        add_deck(user_id, deck_name, colors, leader_id)
        return redirect(url_for('show_decks'))

    # Si ce n'est pas une requête POST, affichez le formulaire d'ajout de deck
    return render_template('add_deck.html', leaders=leaders)




@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        nom = request.form['nom']
        email = request.form['email']
        motDePasse = request.form['motDePasse']  # Devrait être haché pour des raisons de sécurité

        conn = get_user_db_connection()
        try:
            conn.execute('INSERT INTO utilisateurs (nom, email, motDePasse) VALUES (?, ?, ?)',
                         (nom, email, motDePasse))
            conn.commit()
        except sqlite3.IntegrityError:
            return render_template('signup.html', error="Un utilisateur avec cet email existe déjà")
        finally:
            conn.close()

        return redirect(url_for('login'))  # Rediriger vers la page de connexion après l'inscription

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        motDePasse = request.form['motDePasse']

        conn = get_user_db_connection()
        cur = conn.cursor()
        user = cur.execute('SELECT * FROM utilisateurs WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user and user['motDePasse'] == motDePasse:  # Vérification du mot de passe
            session['user_id'] = user['id']  # Stockage de l'ID utilisateur dans la session
            return redirect(url_for('show_decks'))  # Redirection vers la page des decks
        else:
            return render_template('login.html', error="Email ou mot de passe incorrect")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/edit_deck/<int:deck_id>', methods=['GET', 'POST'])
def edit_deck(deck_id):
    if request.method == 'POST':
        # Logique pour ajouter des cartes au deck
        selected_cartes = request.form.getlist('carte_id')
        for carte_id in selected_cartes:
            ajouter_carte_au_deck(deck_id, carte_id)
        return redirect(url_for('show_decks'))

    # Récupérer toutes les cartes disponibles pour les ajouter au deck
    toutes_les_cartes = get_all_cartes()
    cartes_du_deck = get_cartes_from_deck(deck_id)
    return render_template('edit_deck.html', toutes_les_cartes=toutes_les_cartes, cartes_du_deck=cartes_du_deck, deck_id=deck_id)

@app.route('/add_carte', methods=['GET', 'POST'])
def add_carte():
    if request.method == 'POST':
        nom = request.form['nom']
        couleur = request.form['couleur']
        cout = request.form['cout']
        puissance = request.form['puissance']
        attributs = request.form['attributs']
        extension = request.form['extension']
        niveau_counter = request.form['niveau_counter']

        # Traitement de l'image téléchargée
        image = request.files['image']
        if image:
           filename = secure_filename(image.filename)
           image_path = os.path.join('images', filename)  # Enregistrez ce chemin sans 'static/'
           full_image_path = os.path.join(app.static_folder, image_path)
           image.save(full_image_path)

           # Ajoutez la carte à la base de données
           ajouter_carte(nom, couleur, cout, puissance, attributs, extension, niveau_counter, image_path) 

        return redirect(url_for('add_deck_route'))

    return render_template('add_carte.html')

#@app.route('/view_deck/<int:deck_id>')
#def view_deck(deck_id):
#    cartes = get_cartes_from_deck(deck_id)
#    leader = get_leader_from_deck(deck_id)
#    return render_template('view_deck.html', cartes=cartes, leader=leader)
@app.route('/view_deck/<int:deck_id>')
def view_deck(deck_id):
    deck, leader, cartes = get_deck_details(deck_id)
    return render_template('view_deck.html', deck=deck, leader=leader, cartes=cartes)

@app.route('/add_leader', methods=['GET', 'POST'])
def add_leader():
    if request.method == 'POST':
        nom = request.form['nom']
        couleur = request.form['couleur']
        puissance = request.form['puissance']
        effet = request.form['effet']
        attributs = request.form['attributs']
        points_de_vie = request.form['points_de_vie']
        reference = request.form['reference']
        image = request.files['image']
        if image:
            filename = secure_filename(image.filename)
            image_path = os.path.join('images', filename)  # Notez le changement ici
            full_image_path = os.path.join(app.static_folder, image_path)
            image.save(full_image_path)
            
            # Ajouter le leader avec le chemin de l'image
            ajouter_leader(nom, couleur, puissance, effet, attributs, points_de_vie, reference, image_path)

        return redirect(url_for('index'))

    return render_template('add_leader.html')

@app.route('/delete_carte_from_deck/<int:deck_id>/<int:carte_id>')
def delete_carte_from_deck(deck_id, carte_id):
    if session.get('user_id') is None:
        return redirect(url_for('login'))

    supprimer_carte_de_deck(deck_id, carte_id)
    return redirect(url_for('view_deck', deck_id=deck_id))

if __name__ == '__main__':
    app.run(debug=True)
    
