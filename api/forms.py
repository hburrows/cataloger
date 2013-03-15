'''
Created on Mar 14, 2013

@author: howard
'''

from django import forms

class ImageForm(forms.Form):
  image = forms.FileField(
    label='Select a file',
    help_text='max. 42 megabytes'
  )
    