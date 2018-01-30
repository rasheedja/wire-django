from django import forms


class NewWireForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': '3', 'cols': '40'}), label='Message', max_length=280)
