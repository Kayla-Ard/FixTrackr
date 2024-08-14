
from django import forms

class CustomClearableFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True  

    def __init__(self, *args, **kwargs):
        kwargs['attrs'] = kwargs.get('attrs', {})
        kwargs['attrs']['multiple'] = 'multiple'
        super().__init__(*args, **kwargs)

    def value_from_datadict(self, data, files, name):
        return files.getlist(name)


