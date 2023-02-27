from collections import OrderedDict

from flask_wtf import Form
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, BooleanField
from wtforms.validators import DataRequired, Length, Optional, Regexp

from lib.util_wtforms import ModelForm, choices_from_dict

class SearchForm(FlaskForm):
    query = StringField('Query')

class WatchlistBulkDeleteForm(FlaskForm):
    SCOPE = OrderedDict([
        ('all_selected_items', 'All selected items'),
        ('all_search_results', 'All search results')
    ])

    scope = SelectField('Privileges', [DataRequired()],
                        choices=choices_from_dict(SCOPE, prepend_blank=False))

class WatchlistForm(FlaskForm):
    name = StringField('Category Name', [DataRequired()])