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
            ragequit = Exception('AAHHAHAHARRMRRMAHARMARA')
            the_admin = models.Admin.query.filter_by(
                            username=form.username.data).first()
            if the_admin is None:
                raise ragequit
            if not the_admin.check_password(form.password.data):
                raise ragequit
            login_user(the_admin)
            flash("Hello {}, you have successfully logged in.".format(
                the_admin.name), 'success')
            return redirect(url_for(request.args.get('next') or 'admin.index'))
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
        return self.render('admin/photos.html')




class AccountsView(AdminView):
    @expose('/')
    def index(self):
        partners = models.Partner.query.all()
        admins = models.Admin.query.all()
        return self.render('admin/accounts/index.html', partners=partners,
                           admins=admins)

    @expose('/partner/<int:id>/reset-key', methods=['GET', 'POST'])
    def reset_partner_key(self, id):
        partner = models.Partner.query.get_or_404(id)
        if request.form.get('confirm') == 'yes':
            partner.new_key()
            models.db.session.add(partner)
            models.db.session.commit()
            flash('Access key reset for {}'.format(partner.name), 'info')
            return redirect(url_for('.index'))
        return self.render('admin/accounts/reset-key.html', partner=partner)

    @expose('/partner/<int:id>/disable')
    def disable_partner(self, id):
        partner = models.Partner.query.get_or_404(id)
        partner.disabled = True
        models.db.session.add(partner)
        models.db.session.commit()
        flash('Disabled {}. They will not have access to protected content '
              'until re-enabled.'.format(partner.name), 'info')
        return redirect(url_for('.index'))

    @expose('/partner/<int:id>/enable')
    def enable_partner(self, id):
        partner = models.Partner.query.get_or_404(id)
        partner.disabled = False
        models.db.session.add(partner)
        models.db.session.commit()
        flash('Re-enabled access to protected content for {}.'
              .format(partner.name), 'success')
        return redirect(url_for('.index'))

    @expose('/partner/<int:id>/remove')
    def remove_partner(self, id):
        partner = models.Partner.query.get_or_404(id)
        if request.args.get('confirm') == 'yes':
            models.db.session.delete(partner)
            models.db.session.commit()
            flash('Removed partner {}.'.format(partner.name), 'info')
            return redirect(url_for('.index'))
        return self.render('admin/accounts/remove.html', partner=partner)

    @expose('/partner/add', methods=['GET', 'POST'])
    def add_partner(self):
        if request.method == 'POST':
            name = request.form['name']
            partner = models.Partner()
            partner.name = name
            models.db.session.add(partner)
            models.db.session.commit()
            flash('Successfully added "{}" as a partner'.format(partner.name),
                  'success')
            return redirect(url_for('.index'))
        return self.render('admin/accounts/add.html')

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
        return self.render('admin/accounts/add_admin.html', form=form)

    @expose('/admin/<int:id>/new-password', methods=['GET', 'POST'])
    def new_password(self, id):
        the_admin = models.Admin.query.get_or_404(id)
        if request.method == 'POST' and 'password' in request.form:
            the_admin.set_password(request.form['password'])
            models.db.session.add(the_admin)
            models.db.session.commit()
            flash('New password set for {}'.format(the_admin.name), 'info')
            return redirect(url_for('.index'))
        return self.render('admin/accounts/password.html', admin=the_admin)

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
admin.add_view(PhotoView(name='Photos'))
admin.add_view(AccountsView(name='Accounts', endpoint='accounts'))
