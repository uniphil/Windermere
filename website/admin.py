#
# admin.py
#
# administrative controls over the content for the Windermere website
#

from flask import request, flash, redirect, url_for
from flask.ext.login import current_user, login_user, logout_user
from flask.ext.admin import Admin, BaseView, AdminIndexView, expose
from flask.ext.admin.contrib.sqlamodel import ModelView
from website import app, models, forms


class AuthException(Exception):
    pass


class HomeView(AdminIndexView):
    @expose('/')
    def index(self):
        if not (current_user.is_authenticated() and current_user.is_admin):
            return redirect(url_for('.login'))
        return self.render('admin/overview.html')

    @expose('/login', methods=['GET', 'POST'])
    def login(self):
        form = forms.LoginForm(request.form)
        if form.validate_on_submit():
            try:
                the_admin = models.Admin.query.filter_by(
                                username=form.username.data).first()
                if the_admin is None:
                    form.username.errors.append('Username not found :|')
                    raise AuthException
                if not the_admin.check_password(form.password.data):
                    form.password.errors.append('Password did not check out :(')
                    raise AuthException
                login_user(the_admin)
                flash("Hello {}, you have successfully logged in.".format(
                    the_admin.name), 'success')
                return redirect(url_for(request.args.get('next') or
                                        'admin.index'))
            except AuthException:
                pass
        return self.render('admin/login.html', form=form)

    @expose('/logout')
    def logout(self):
        logout_user()
        return redirect(url_for('home'))


class AdminView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated() and current_user.is_admin


class DocumentView(AdminView):
    @expose('/')
    def index(self):
        return self.render('admin/documents.html')




class PhotoView(AdminView):
    @expose('/')
    def index(self):
        photos = models.ScenicPhoto.query.all()
        return self.render('admin/photos/index.html', photos=photos)

    @expose('/photo/add', methods=['GET', 'POST'])
    def add_photo(self):
        form = forms.ScenicPhotoForm(request.form)
        if form.validate_on_submit():
            new_photo = models.ScenicPhoto()
            new_photo.title = request.form['title']
            new_photo.description = request.form['description']
            models.db.session.add(new_photo)
            models.db.session.commit()
            flash('Saved new photo "{}"'.format(new_photo.title), 'success')
            return redirect(url_for('.index'))
        return self.render('admin/photos/add_edit.html', form=form,
                           verb='Add', ico='plus', action='Save')



class AccountsView(AdminView):
    @expose('/')
    def index(self):
        partners = models.Partner.query.all()
        admins = models.Admin.query.all()
        return self.render('admin/accounts/index.html', partners=partners,
                           admins=admins)

    @expose('/partner/<int:id>/edit', methods=['GET', 'POST'])
    def edit_partner(self, id):
        partner = models.Partner.query.get_or_404(id)
        errors = []
        if request.method == 'POST':
            if request.form.get('key'):
                from datetime import datetime
                partner.key = request.form['key']
                partner.last_keychange = datetime.now()
                models.db.session.add(partner)
                models.db.session.commit()
                flash('Saved new key for {}'.format(partner.name), 'info')
                return redirect(url_for('.index'))
            else:
                errors.append('Please set a key for partner access...')
        return self.render('admin/accounts/edit_partner.html', verb='Edit',
                           action='set', ico='pencil', key=partner.key,
                           name=partner.name)

    @expose('/admin/add', methods=['GET', 'POST'])
    def add_admin(self):
        form = forms.AdminForm(request.form)
        if form.validate_on_submit():
            new_admin = models.Admin()
            new_admin.name = form.name.data
            new_admin.username = form.username.data
            new_admin.set_password(form.password.data)
            models.db.session.add(new_admin)
            models.db.session.commit()
            flash('Successfully added new admin {}.'.format(new_admin.name),
                  'success')
            return redirect(url_for('.index'))
        return self.render('admin/accounts/add_admin.html', form=form,
                           verb='Add', action='Add', ico='plus')

    @expose('/admin/<int:id>/edit', methods=['GET', 'POST'])
    def edit_admin(self, id):
        the_admin = models.Admin.query.get_or_404(id)
        form = forms.AdminForm(request.form, the_admin)
        form.password.validators = []
        if form.validate_on_submit():
            the_admin.name = form.name.data
            the_admin.username = form.username.data
            if form.password.data:
                the_admin.set_password(form.password.data)
            models.db.session.add(the_admin)
            models.db.session.commit()
            flash('Successfully saved settings for {}.'.format(the_admin.name),
                  'info')
            return redirect(url_for('.index'))
        return self.render('admin/accounts/add_admin.html', form=form,
                           verb='Edit', action='Save', ico='pencil')

    @expose('/admin/<int:id>/disable')
    def disable_admin(self, id):
        the_admin = models.Admin.query.get_or_404(id)
        the_admin.disabled = True
        models.db.session.add(the_admin)
        models.db.session.commit()
        flash('Disabled {}. They will be restricted to public access only.'
              .format(the_admin.name), 'info')
        return redirect(url_for('.index'))

    @expose('/admin/<int:id>/enable')
    def enable_admin(self, id):
        the_admin = models.Admin.query.get_or_404(id)
        the_admin.disabled = False
        models.db.session.add(the_admin)
        models.db.session.commit()
        flash('Re-enabled administrator {}.'.format(the_admin.name), 'success')
        return redirect(url_for('.index'))

    @expose('/admin/<int:id>/remove', methods=['GET', 'POST'])
    def remove_admin(self, id):
        the_admin = models.Admin.query.get_or_404(id)
        if request.form.get('confirm') == 'yes':
            models.db.session.delete(the_admin)
            models.db.session.commit()
            flash('Removed administrator {}.'.format(the_admin.name), 'info')
            return redirect(url_for('.index'))
        return self.render('admin/accounts/remove_admin.html', admin=the_admin)



admin = Admin(app, name='Windermere Admin', index_view=HomeView(name="Overview"))
admin.add_view(DocumentView(name='Documents'))
admin.add_view(PhotoView(name='Photos', endpoint='photos'))
admin.add_view(AccountsView(name='Accounts', endpoint='accounts'))
