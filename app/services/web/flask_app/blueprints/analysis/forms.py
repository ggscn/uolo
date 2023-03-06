from wtforms import Form, SelectField, StringField

class SearchForm(Form):
    analysis_label = SelectField('Analysis Label')
    indicator = SelectField('Indicator')
    period = SelectField('Rolling Periods')
    filter_indicator = SelectField('Filter Indicator')
    filter_indicator_label = SelectField('Analysis Label')
    filter_percentile = StringField('Percentile Threshold')