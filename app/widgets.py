
from django import forms



class CustomClearableFileInput(forms.ClearableFileInput):
    def value_from_datadict(self, data, files, name):
        return files.get(name)  # Return a single file instead of a list



