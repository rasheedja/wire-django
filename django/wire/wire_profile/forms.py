from django import forms


class NewWireForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': '3', 'cols': '40'}), label='Message', max_length=280)


class SearchForm(forms.Form):
    search_choices = (
        ('true', 'Wires'),
        ('false', 'Users')
    )
    search_query = forms.CharField(label='Search Query')
    is_wire_search = forms.CharField(widget=forms.Select(choices=search_choices), label='Search For?')
