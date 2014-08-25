'''
Created on 2014-8-13

@author: gaoxiao
'''

from django import forms

class SearchForm(forms.Form):
    q = forms.CharField(
        widget=forms.TextInput(attrs={'class':'form-control'})
    )
