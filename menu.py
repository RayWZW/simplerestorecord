from flask import Blueprint, render_template, session

menu_blueprint = Blueprint('menu', __name__)

@menu_blueprint.route('/menu')
def menu():
    if 'logged_in' not in session:
        return redirect('/login')  # Redirect to login if not logged in
    return render_template('menu.html', username=session.get('username'))  # Pass username to the template
