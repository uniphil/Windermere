#
# admin.py
#
# administrative controls over the content for the Windermere website
#

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


class UserView(ModelView):
    column_list = ('username')


admin.add_view(ModelView(models.User, models.db.session, name='Users'))
