from django import forms
from django.utils.datastructures import MultiValueDict

class CustomClearableFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

    def value_from_datadict(self, data, files, name):
        if isinstance(files, MultiValueDict):
            file_list = files.getlist(name)
            return file_list
        return files.get(name)

    def use_required_attribute(self, initial):
        return False










