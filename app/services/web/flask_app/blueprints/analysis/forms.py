from wtforms import Form, SelectField, StringField

class SearchForm(Form):
    analysis_label = SelectField('Analysis Label')
    indicator = SelectField('Indicator')
    period = SelectField('Rolling Periods')
    f_indicator = SelectField('Filter Indicator')
    f_indicator_label = SelectField('Analysis Label')
    f_percentile = StringField('Percentile Threshold')