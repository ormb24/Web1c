from flask import render_template, session, redirect, url_for, request, flash

import my_app
from . import main
from flask_login import login_required, current_user
from .forms import CreateEnigmaForm, RiddleForm
from .. import db
from ..models import Enigma, Riddle

@main.route('/')
def index():
    return infos()

@main.route('/infos')
def infos():
    return render_template('main/infos.html')

@main.route('/liste', methods=['GET','POST'])
@login_required
def list_enigmas():
    page = request.args.get('page',1,type=int)
    pagination = Enigma.query.order_by(Enigma.id.asc()).paginate(page=page,per_page=5)
    enigmas = pagination.items
    return render_template('main/list_enigma.html',enigmas=enigmas, pagination=pagination)
    ##enigmas = Enigma.query.all()
    #return 'Liste des énigmes'
    ##return render_template('main/list_enigma.html', enigmas=enigmas)

@main.route('/list_riddle', methods=['GET','POST'])
#@login_required
def list_riddles():
    #page = request.args.get('page', 1, type=int)
    #pagination = Enigma.query.order_by(Enigma.id.asc()).paginate(page=page, per_page=5)
    #enigmas = pagination.items
    riddles = Riddle.query.order_by(Riddle.id.asc())
    return render_template('main/list_riddle.html', riddles=riddles)

@main.route('/kamoulox', methods=['GET','POST'])
@login_required
def create_enigmas():
    #if request.method == "GET":
    #    session['next'] = request.args.get('next')

    isError=False
    form = CreateEnigmaForm()

    if request.method == "POST":
        if form.validate_on_submit():
            #return "Enigme : {}; Reponse : {}, Level : {}".format(enigma,response,level)
            try:
                enigma=Enigma(form.enigma.data, form.response.data, int(form.level.data))
                db.session.add(enigma)
                db.session.commit()
            except BaseException as e:
                isError=True
                flash('Un problème est survenu lors de l\'insertion dans la base de données : '+str(e))

            #next = session.get('next')
            #if next is None or not next.startswith('/'):
            #    next = url_for('main.index')
            #return redirect(next)
        else:
            isError=True

        if not isError:
            flash('Enigme ajoutée avec succès')
        else:
            flash("L\'ajout de l\'enigme a échoué !")
            #return render_template('main/create_enigma.html', form=form)
    return render_template('main/create_enigma.html', form=form)
@main.route('/level', methods=['GET'])
@login_required
def update_level():
    id = request.args.get("id")
    enigma = Enigma.query.filter_by(id=id).first()
    if request.args.get("direction") == 'up':
        enigma.set_level(enigma.level +1)
    elif enigma.level > 0:
         enigma.set_level(enigma.level -1)
    else:
        flash("Le niveau ne peut être inférieur à 0 !")
    db.session.commit()
    return list_enigmas()


@main.route('/create_riddle', methods=['GET','POST'])
def create_riddle():
    form = RiddleForm()
    form.id.data = 0
    return render_template("main/create_riddle.html",form=form, action="Create")

@main.route('/update_riddle', methods=['GET'])
def update_riddle():
    id = request.args.get('id')
    form = RiddleForm()
    try:
        riddle = Riddle.query.filter_by(id=id).first()
        form.id.data = riddle.id
        form.riddle.data = riddle.riddle
        form.answer.data = riddle.answer
        form.level.data = riddle.level
    except BaseException as e:
        flash("L'énigme n'a pu être trouvée en DB : "+str(e))
    return render_template("main/create_riddle.html", form=form, action="Update")

@main.route('/save_riddle',methods=['POST'])
def save_riddle():
    form = RiddleForm()

    id = int(form.id.data)
    riddle = form.riddle.data
    answer = form.answer.data
    level = int(form.level.data)

    if id != 0:
        riddle_record = Riddle.query.filter_by(id=id).first()
        message = "L'énigme a été modifiée !"
        action = "Update"
    else:
        riddle_record = Riddle(riddle,answer,level)
        message = "L'énigme a été créée !"
        action = "Create"

    if form.validate_on_submit():
        riddle_record.riddle = riddle
        riddle_record.answer = answer
        riddle_record.level = level
        db.session.add(riddle_record)
        db.session.commit()
        flash(message, 'Success')
        return redirect(url_for('main.create_riddle')) #To avoid re-submitting a post request on 'Refresh page'.
    else:
        return render_template("main/create_riddle.html",form=form,action=action)


@main.route('/delete_riddle', methods=['GET'])
def delete_riddle():
    id = request.args.get('id')
    try:
        riddle = Riddle.query.filter_by(id=id).first()
        db.session.delete(riddle)
        db.session.commit()
    except BaseException as e:
        flash("L'énigme n'a pas été supprimée : "+ str(e))
    return list_riddles()

@main.route('/bootstrap')
def bootstrap():
    return render_template('main/bootstrap_test.html')

