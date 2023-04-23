from flask import render_template, redirect, url_for, request, flash, abort

from . import main
from flask_login import login_required, current_user, logout_user
from .forms import CreateEnigmaForm, RiddleForm, ClueForm
from .. import db
from ..models import Enigma, Riddle, Clue

@main.route('/')
@login_required
def index():
    #return infos()
    return list_riddle()
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


""" ********************
    Controller : Riddles
    ********************
"""
@main.route('/list_riddle', methods=['GET','POST'])
@login_required
def list_riddle():
    page = request.args.get('page', 1, type=int)
    if current_user.blocked:
        flash('Your account has been blocked by an administrator.', 'Danger')
        logout_user()
        return redirect(url_for('auth.login'))

    if current_user.admin:
        #riddles = Riddle.query.all()
        pagination = db.paginate(db.select(Riddle).order_by(Riddle.id.asc()), per_page=5)
    else:
        #riddles = Riddle.query.filter_by(user_id=current_user.id).all()
        pagination = db.paginate(db.select(Riddle).filter_by(user_id=current_user.id).order_by(Riddle.id.asc()), per_page=5)

    riddles = pagination.items
    return render_template('main/list_riddle.html', riddles=riddles, current_user=current_user, pagination=pagination)

@main.route('/create_riddle', methods=['GET','POST'])
@login_required
def create_riddle():
    form = RiddleForm()
    form.id.data = 0
    return render_template("main/create_riddle.html",form=form, current_user=current_user, action="Create")

@main.route('/update_riddle', methods=['GET'])
@login_required
def update_riddle():
    if current_user.blocked:
        flash('Your account has been blocked by an administrator.', 'Danger')
        logout_user()
        return redirect(url_for('auth.login'))

    id = request.args.get('id')
    riddle = Riddle.query.filter_by(id=id).first()

    if not (current_user.admin) and not (riddle.user_id == current_user.id):
        abort(403)

    form = RiddleForm()

    form.id.data = riddle.id
    form.riddle.data = riddle.riddle
    form.answer.data = riddle.answer
    form.level.data = riddle.level

    return render_template("main/create_riddle.html", form=form, current_user=current_user, action="Update")

@main.route('/save_riddle',methods=['POST'])
@login_required
def save_riddle():
    if current_user.blocked:
        flash('Your account has been blocked by an administrator.', 'Danger')
        logout_user()
        return redirect(url_for('auth.login'))

    form = RiddleForm()

    id = int(form.id.data)
    riddle = form.riddle.data
    answer = form.answer.data
    level = int(form.level.data)

    if id != 0:
        riddle_record = Riddle.query.filter_by(id=id).first()
        user_id = riddle_record.user_id
        message = "L'énigme a été modifiée !"
        action = "Update"
    else:
        riddle_record = Riddle(riddle,answer,level,current_user.id)
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
        return render_template("main/create_riddle.html",form=form, current_user=current_user, action=action)


@main.route('/delete_riddle', methods=['GET'])
@login_required
def delete_riddle():
    if current_user.blocked:
        flash('Your account has been blocked by an administrator.', 'Danger')
        logout_user()
        return redirect(url_for('auth.login'))

    id = request.args.get('id')
    user_id = request.args.get('user_id')
    riddle = Riddle.query.filter_by(id=id).first()

    if not (current_user.admin) and not (riddle.user_id == current_user.id):
        abort(403)

    try:
        db.session.delete(riddle)
        db.session.commit()
    except BaseException as e:
        flash("L'énigme n'a pas été supprimée : "+ str(e))

    return redirect('/?id='+str(user_id), code=302)

@main.route('/level', methods=['GET'])
@login_required
def update_level():
    id = request.args.get("id")
    riddle = Riddle.query.filter_by(id=id).first()

    if request.args.get("direction") == 'up':
        riddle.set_level(riddle.level + 1)
    elif riddle.level > 0:
        riddle.set_level(riddle.level - 1)
    else:
        flash("Le niveau ne peut être inférieur à 0 !")
    db.session.commit()
    return list_riddle()

@main.route('/clue', methods=['GET'])
@login_required
def clue():
    if current_user.blocked:
        flash('Your account has been blocked by an administrator.', 'Danger')
        logout_user()
        return redirect(url_for('auth.login'))

    riddle_id = request.args.get('riddle_id')
    clue = Clue.query.filter_by(riddle_id=riddle_id).first()
    form = ClueForm()

    if clue:
        template = "main/update_clue.html"
        form.id.data = clue.id
        form.clue.data = clue.clue
        form.riddle.data = clue.riddle.riddle
        form.riddle_id.data = riddle_id
    else:
        template = "main/create_clue.html"
        form.id.data = 0
        form.clue.data= ""
        riddle = Riddle.query.filter_by(id=riddle_id).first()
        form.riddle.data = riddle.riddle
        form.riddle_id.data = riddle_id

    if not (current_user.admin) and not (riddle.user_id == current_user.id):
        abort(403)

    return render_template(template, form=form)

@main.route('/save_clue',methods=['POST'])
@login_required
def save_clue():
    if current_user.blocked:
        flash('Your account has been blocked by an administrator.', 'Danger')
        logout_user()
        return redirect(url_for('auth.login'))

    form = ClueForm()

    id = int(form.id.data)
    riddle_id=int(form.riddle_id.data)
    clue = form.clue.data

    if id != 0:
        clue_record = Clue.query.filter_by(id=id).first()
        message = "L'énigme a été modifiée !"
    else:
        clue_record = Clue(clue,riddle_id)
        message = "L'énigme a été créée !"

    if form.validate_on_submit():
        clue_record.clue = clue
        clue_record.riddle_id = riddle_id
        db.session.add(clue_record)
        db.session.commit()
        flash(message, 'Success')
        return redirect(url_for('main.list_riddle')) #To avoid re-submitting a post request on 'Refresh page'.
    else:
        return render_template("main/create_clue.html",form=form)

