from flask import Flask,render_template, request, redirect, url_for, flash, session, logging
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import MySQLdb.cursors
import re

app = Flask(__name__)
app.secret_key="Secret Key"
 
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root@localhost/vocarna'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
 
db=SQLAlchemy(app)

class Zaposlenik(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ime = db.Column(db.String(50), unique=True, nullable=False)
    prezime= db.Column(db.String(50))
    adresa= db.Column(db.String(50))
    email = db.Column(db.String(50))
    telefon=db.Column(db.String(50))
    racuni = db.relationship('Racun', backref='zaposlenik')

    def __init__(self, ime, prezime, adresa,email, telefon ):
        self.ime=ime
        self.prezime=prezime
        self.adresa=adresa
        self.email=email
        self.telefon=telefon

class Kupac(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    naziv = db.Column(db.String(50), unique=True, nullable=False)
    adresa= db.Column(db.String(50))
    telefon=db.Column(db.String(50))
    racuni = db.relationship('Racun', backref='kupac')

    def __init__(self, naziv, adresa, telefon ):
        self.naziv=naziv
        self.adresa=adresa
        self.telefon=telefon

class Dostava(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    naziv = db.Column(db.String(50), unique=True, nullable=False)
    racuni = db.relationship('Racun', backref='dostava')

    def __init__(self, naziv):
        self.naziv=naziv

class Drzava(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    naziv = db.Column(db.String(50), unique=True, nullable=False)
    gradovi = db.relationship('Grad', backref='drzava')

    def __init__(self, naziv):
        self.naziv=naziv

class Grad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    naziv = db.Column(db.String(50), unique=True, nullable=False)
    broj_stanovnika=db.Column(db.String(50))
    drzava_id = db.Column(db.Integer, db.ForeignKey('drzava.id'))
    voce = db.relationship('Voce', backref='grad')

    def __init__(self, naziv, broj_stanovnika, drzava_id):
        self.naziv=naziv
        self.broj_stanovnika=broj_stanovnika
        self.drzava_id = drzava_id

class Voce(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    naziv = db.Column(db.String(50), unique=True, nullable=False)
    cijena=db.Column(db.String(50))
    grad_id = db.Column(db.Integer, db.ForeignKey('grad.id'))
    stavka_racuna = db.relationship('Stavka_racuna', backref='voce')
    

    def __init__(self, naziv, cijena, grad_id):
        self.naziv=naziv
        self.cijena=cijena
        self.grad_id = grad_id

class Racun(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    broj_racuna = db.Column(db.String(50), unique=True, nullable=False)
    kolicina=db.Column(db.String(50))
    ukupna_cijena=db.Column(db.String(50))
    dostava_id = db.Column(db.Integer, db.ForeignKey('dostava.id'))
    kupac_id = db.Column(db.Integer, db.ForeignKey('kupac.id'))
    zaposlenik_id = db.Column(db.Integer, db.ForeignKey('zaposlenik.id'))
    stavka_racuna = db.relationship('Stavka_racuna', backref='racun')


    def __init__(self, broj_racuna, kolicina, ukupna_cijena, dostava_id, kupac_id, zaposlenik_id):
        self.broj_racuna=broj_racuna
        self.kolicina=kolicina
        self.ukupna_cijena=ukupna_cijena
        self.dostava_id= dostava_id
        self.kupac_id=kupac_id
        self.zaposlenik_id=zaposlenik_id

class Stavka_racuna(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datum_isporuke = db.Column(db.String(50), unique=True, nullable=False)
    kolicina=db.Column(db.String(50))
    voce_id = db.Column(db.Integer, db.ForeignKey('voce.id'))
    racun_id = db.Column(db.Integer, db.ForeignKey('racun.id'))

    def __init__(self, datum_isporuke, kolicina, voce_id, racun_id):
        self.datum_isporuke=datum_isporuke
        self.kolicina=kolicina
        self.voce_id=voce_id
        self.racun_id=racun_id



class Korisnik(db.Model):
    __tablename__ = 'korisnici'
    id = db.Column(db.Integer, primary_key=True)
    ime = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    lozinka = db.Column(db.String(200), nullable=False)

    def __init__(self, ime, email, lozinka):
        self.ime = ime
        self.email = email
        self.lozinka = generate_password_hash(lozinka)


@app.route('/registracija', methods=['GET', 'POST'])
def registracija():
    if request.method == 'POST':
        ime = request.form['ime']
        email = request.form['email']
        lozinka = request.form['lozinka']
        korisnik = Korisnik(ime=ime, email=email, lozinka=lozinka)
        db.session.add(korisnik)
        db.session.commit()
        return redirect(url_for('Login'))
    return render_template('registracija.html')


@app.route('/prijava', methods=['GET', 'POST'])
def prijava():
    if request.method == 'POST':
        email = request.form['email']
        lozinka = request.form['lozinka']
        korisnik = Korisnik.query.filter_by(email=email).first()
        if korisnik and check_password_hash(korisnik.lozinka, lozinka):
            session['korisnik_id'] = korisnik.id
            return redirect(url_for('Index'))
        else:
            # flash('Krivo korisničko ime ili lozinka!')
            return render_template('prijava.html')

@app.route('/odjava')
def odjava():
    session.pop('korisnik_id', None)
    # flash('Odjavljeni ste!')
    return redirect(url_for('Login'))

@app.route('/')
def Login():
    return render_template("prijava.html")

@app.route('/index')
def Index():
    return render_template("index.html")

@app.route('/employee')
def Employee():
    all_zaposlenici=Zaposlenik.query.all()
    return render_template("employee.html", zaposlenici=all_zaposlenici)

@app.route('/insert', methods=['POST'])
def insert():
    if request.method == 'POST':
        ime=request.form['ime']
        prezime=request.form['prezime']
        adresa=request.form['adresa']
        email=request.form['email'] 
        telefon=request.form['telefon']

        my_zaposlenik=Zaposlenik(ime, prezime, adresa, email, telefon)
        db.session.add(my_zaposlenik)
        db.session.commit()

        flash("Uspješno ste dodali zaposlenika!")

        return redirect(url_for('Employee'))

@app.route('/update', methods=['GET', 'POST'])
def update():

    if request.method == 'POST':

        my_zaposlenik=Zaposlenik.query.get(request.form.get('id'))

        my_zaposlenik.ime=request.form['ime']
        my_zaposlenik.prezime=request.form['prezime']
        my_zaposlenik.adresa=request.form['adresa']
        my_zaposlenik.email=request.form['email']
        my_zaposlenik.telefon=request.form['telefon']
  
        db.session.commit()
        flash("Uspješno ste anžurirali podatke!")

        return redirect(url_for('Employee'))

@app.route('/delete/<id>/', methods=['GET', 'POST'])
def delete(id):
    my_zaposlenik=Zaposlenik.query.get(id)
    db.session.delete(my_zaposlenik)
    db.session.commit()
    flash("Uspješno ste izbrisali zaposlenika!")

    return redirect(url_for('Employee'))



@app.route('/customer')
def Customer():
    all_kupci=Kupac.query.all()
    return render_template("customer.html", kupci=all_kupci)

@app.route('/insert1', methods=['POST'])
def insert1():
    if request.method == 'POST':
        naziv=request.form['naziv']
        adresa=request.form['adresa']
        telefon=request.form['telefon']

        my_kupac=Kupac(naziv, adresa, telefon)
        db.session.add(my_kupac)
        db.session.commit()

        flash("Uspješno ste dodali kupca!")

        return redirect(url_for('Customer'))

@app.route('/update1', methods=['GET', 'POST'])
def update1():

    if request.method == 'POST':

        my_kupac=Kupac.query.get(request.form.get('id'))

        my_kupac.naziv=request.form['naziv']
        my_kupac.adresa=request.form['adresa']
        my_kupac.telefon=request.form['telefon']
  
        db.session.commit()
        flash("Uspješno ste anžurirali podatke!")

        return redirect(url_for('Customer'))

@app.route('/delete1/<id>/', methods=['GET', 'POST'])
def delete1(id):
    my_kupac=Kupac.query.get(id)
    db.session.delete(my_kupac)
    db.session.commit()
    flash("Uspješno ste izbrisali kupca!")

    return redirect(url_for('Customer'))



@app.route('/state')
def State():
    all_drzave=Drzava.query.all()
    return render_template("state.html", drzave=all_drzave)

@app.route('/insert2', methods=['POST'])
def insert2():
    if request.method == 'POST':
        naziv=request.form['naziv']

        my_drzava=Drzava(naziv)
        db.session.add(my_drzava)
        db.session.commit()

        flash("Uspješno ste dodali državu!")

        return redirect(url_for('State'))

@app.route('/update2', methods=['GET', 'POST'])
def update2():

    if request.method == 'POST':

        my_drzava=Drzava.query.get(request.form.get('id'))

        my_drzava.naziv=request.form['naziv']
  
        db.session.commit()
        flash("Uspješno ste anžurirali podatke!")

        return redirect(url_for('State'))

@app.route('/delete2/<id>/', methods=['GET', 'POST'])
def delete2(id):
    my_drzava=Drzava.query.get(id)
    db.session.delete(my_drzava)
    db.session.commit()
    flash("Uspješno ste izbrisali državu!")

    return redirect(url_for('State'))



@app.route('/delivery')
def Delivery():
    all_dostave=Dostava.query.all()
    return render_template("delivery.html", dostave=all_dostave)

@app.route('/insert3', methods=['POST'])
def insert3():
    if request.method == 'POST':
        naziv=request.form['naziv']

        my_dostava=Dostava(naziv)
        db.session.add(my_dostava)
        db.session.commit()

        flash("Uspješno ste dodali dostavu!")

        return redirect(url_for('Delivery'))

@app.route('/update3', methods=['GET', 'POST'])
def update3():

    if request.method == 'POST':

        my_dostava=Dostava.query.get(request.form.get('id'))

        my_dostava.naziv=request.form['naziv']
  
        db.session.commit()
        flash("Uspješno ste anžurirali podatke!")

        return redirect(url_for('Delivery'))

@app.route('/delete3/<id>/', methods=['GET', 'POST'])
def delete3(id):
    my_dostava=Dostava.query.get(id)
    db.session.delete(my_dostava)
    db.session.commit()
    flash("Uspješno ste izbrisali dostavu!")

    return redirect(url_for('Delivery'))



@app.route('/city')
def City():
    all_gradovi=Grad.query.all()
    all_drzave=Drzava.query.all()
    return render_template("city.html", gradovi=all_gradovi, drzave=all_drzave)

@app.route('/insert4', methods=['POST'])
def insert4():
    if request.method == 'POST':
        naziv=request.form['naziv']
        broj_stanovnika=request.form['broj_stanovnika']
        drzava_id=request.form['drzava']

        my_grad=Grad(naziv,broj_stanovnika,drzava_id)
        db.session.add(my_grad)
        db.session.commit()

        flash("Uspješno ste dodali grad!")

        return redirect(url_for('City'))

@app.route('/update4', methods=['GET', 'POST'])
def update4():

    if request.method == 'POST':

        my_grad=Grad.query.get(request.form.get('id'))

        my_grad.naziv=request.form['naziv']
        my_grad.broj_stanovnika=request.form['broj_stanovnika']
        my_grad.drzava_id = request.form['drzava']
        my_grad.drzava_id=request.form['drzava']
  
        db.session.commit()
        flash("Uspješno ste anžurirali podatke!")

        return redirect(url_for('City'))

@app.route('/delete4/<id>/', methods=['GET', 'POST'])
def delete4(id):
    my_grad=Grad.query.get(id)
    db.session.delete(my_grad)
    db.session.commit()
    flash("Uspješno ste izbrisali grad!")

    return redirect(url_for('City'))



@app.route('/fruit')
def Fruit():
    all_voce = Voce.query.group_by(Voce.naziv).all()
    all_gradovi=Grad.query.all()
    return render_template("fruit.html", voce=all_voce, gradovi=all_gradovi)

@app.route('/insert5', methods=['POST'])
def insert5():
    if request.method == 'POST':
        naziv=request.form['naziv']
        cijena=request.form['cijena']
        grad_id=request.form['grad']

        my_voce=Voce(naziv,cijena, grad_id)
        db.session.add(my_voce)
        db.session.commit()

        flash("Uspješno ste dodali voće!")

        return redirect(url_for('Fruit'))

@app.route('/update5', methods=['GET', 'POST'])
def update5():

    if request.method == 'POST':

        my_voce=Voce.query.get(request.form.get('id'))

        my_voce.naziv=request.form['naziv']
        my_voce.cijena=request.form['cijena']
        my_voce.grad_id=request.form['grad']
  
        db.session.commit()
        flash("Uspješno ste anžurirali podatke!")

        return redirect(url_for('Fruit'))

@app.route('/delete5/<id>/', methods=['GET', 'POST'])
def delete5(id):
    my_voce=Voce.query.get(id)
    db.session.delete(my_voce)
    db.session.commit()
    flash("Uspješno ste izbrisali voće!")

    return redirect(url_for('Fruit'))

@app.route('/bill')
def Bill():
    all_racuni=Racun.query.all()
    all_dostave=Dostava.query.all()
    all_kupci=Kupac.query.all()
    all_zaposlenici=Zaposlenik.query.all()
    
    return render_template("bill.html", racuni=all_racuni, dostave=all_dostave, kupci=all_kupci, zaposlenici=all_zaposlenici)

@app.route('/insert6', methods=['POST'])
def insert6():
    if request.method == 'POST':
        broj_racuna=request.form['broj_racuna']
        kolicina=request.form['kolicina']
        ukupna_cijena=request.form['ukupna_cijena']
        dostava_id=request.form['dostava']
        kupac_id=request.form['kupac']
        zaposlenik_id=request.form['zaposlenik']

        my_racun=Racun(broj_racuna,kolicina, ukupna_cijena, dostava_id, kupac_id, zaposlenik_id)
        db.session.add(my_racun)
        db.session.commit()

        flash("Uspješno ste dodali račun!")

        return redirect(url_for('Bill'))

@app.route('/update6', methods=['GET', 'POST'])
def update6():

    if request.method == 'POST':

        my_racun=Racun.query.get(request.form.get('id'))

        my_racun.broj_racuna=request.form['broj_racuna']
        my_racun.kolicina=request.form['kolicina']
        my_racun.ukupna_cijena=request.form['ukupna_cijena']
        my_racun.dostava_id=request.form['dostava']
        my_racun.kupac_id=request.form['kupac']
        my_racun.zaposlenik_id=request.form['zaposlenik']
  
        db.session.commit()
        flash("Uspješno ste anžurirali podatke!")

        return redirect(url_for('Bill'))

@app.route('/delete6/<id>/', methods=['GET', 'POST'])
def delete6(id):
    my_racun=Racun.query.get(id)
    db.session.delete(my_racun)
    db.session.commit()
    flash("Uspješno ste izbrisali račun!")

    return redirect(url_for('Bill'))



@app.route('/item_bill')
def Item_bill():
    all_stavke=Stavka_racuna.query.all()
    all_racuni=Racun.query.all()
    all_voce=Voce.query.all()
    return render_template("item_bill.html", stavke=all_stavke, racuni=all_racuni, voce=all_voce)


@app.route('/insert7', methods=['POST'])
def insert7():
    if request.method == 'POST':
        datum_isporuke=request.form['datum_isporuke']
        kolicina=request.form['kolicina']
        racun_id=request.form['racun_id']
        voce_id=request.form['voce_id']

        my_stavka=Stavka_racuna(datum_isporuke,kolicina, voce_id, racun_id)
        db.session.add(my_stavka)
        db.session.commit()

        flash("Uspješno ste dodali stavku!")

        return redirect(url_for('Item_bill'))

@app.route('/update7', methods=['GET', 'POST'])
def update7():

    if request.method == 'POST':

        my_stavka=Stavka_racuna.query.get(request.form.get('id'))

        my_stavka.datum_isporuke=request.form['datum_isporuke']
        my_stavka.kolicina=request.form['kolicina']
        my_stavka.racun_id=request.form['racun_id']
        my_stavka.voce_id=request.form['voce_id']
  
        db.session.commit()
        flash("Uspješno ste anžurirali podatke!")

        return redirect(url_for('Item_bill'))

@app.route('/delete7/<id>/', methods=['GET', 'POST'])
def delete7(id):
    my_stavka=Stavka_racuna.query.get(id)
    db.session.delete(my_stavka)
    db.session.commit()
    flash("Uspješno ste izbrisali stavku!")

    return redirect(url_for('Item_bill'))

with app.app_context():
    db.create_all()
    app.run(debug=True)


