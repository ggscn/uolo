from wtforms import Form, SelectField

class SearchForm(Form):
    analysis_label = SelectField('Indicator')