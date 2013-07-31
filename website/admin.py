#
# admin.py
#
# administrative controls over the content for the Windermere website
#

from flask import request, flash, redirect, url_for
from flask.ext.admin import Admin, BaseView, expose
from flask.ext.admin.contrib.sqlamodel import ModelView
from website import app, models
admin = Admin(app, name='Windermere Admin')


class DocumentView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/documents.html')


admin.add_view(DocumentView(name='Documents'))


class PhotoView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/photos.html')

admin.add_view(PhotoView(name='Photos'))



class AccountsView(BaseView):
    @expose('/')
    def index(self):
        partners = models.Partner.query.all()
        admins = models.Admin.query.all()
        return self.render('admin/accounts/index.html', partners=partners,
                           admins=admins)

    @expose('/partner/<int:id>/reset-key', methods=['GET', 'POST'])
    def reset_partner_key(self, id):
        partner = models.Partner.query.get(id)
        if request.form.get('confirm') == 'yes':
            partner.new_key()
            models.db.session.add(partner)
            models.db.session.commit()
            flash('Access key reset for {}'.format(partner.name))
            return redirect(url_for('.index'))
        return self.render('admin/accounts/reset-key.html', partner=partner)

    @expose('/partner/<int:id>/disable')
    def disable_partner(self, id):
        partner = models.Partner.query.get(id)
        partner.disabled = True
        models.db.session.add(partner)
        models.db.session.commit()
        flash('Disabled {}. They will not have access to protected content '
              'until re-enabled.'.format(partner.name))
        return redirect(url_for('.index'))

    @expose('/partner/<int:id>/enable')
    def enable_partner(self, id):
        partner = models.Partner.query.get(id)
        partner.disabled = False
        models.db.session.add(partner)
        models.db.session.commit()
        flash('Re-enabled access to protected content for {}.'
              .format(partner.name), 'info')
        return redirect(url_for('.index'))

    @expose('/partner/<int:id>/remove')
    def remove_partner(self, id):
        partner = models.Partner.query.get(id)
        if request.args.get('confirm') == 'yes':
            models.db.session.delete(partner)
            models.db.session.commit()
            flash('Deleted partner {}.'.format(partner.name))
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


admin.add_view(AccountsView(name='Accounts', endpoint='accounts'))
