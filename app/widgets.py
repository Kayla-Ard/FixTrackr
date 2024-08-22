from django import forms

class CustomClearableFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True  # This enables the widget to accept multiple files

    def value_from_datadict(self, data, files, name):
        if self.allow_multiple_selected:
            return files.getlist(name)  # Return a list of files instead of a single file
        return super().value_from_datadict(data, files, name)

    def use_required_attribute(self, initial):
        return False  # Override to prevent issues with the required attribute on multiple file inputs





