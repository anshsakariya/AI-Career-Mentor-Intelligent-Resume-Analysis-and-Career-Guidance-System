from django import forms
from .models import Resume

class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control form-control-custom', 'accept': '.pdf'})
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file:
            raise forms.ValidationError("Please select a valid PDF file to upload.")

        # Check extension
        if not file.name.lower().endswith('.pdf'):
            raise forms.ValidationError("Only PDF files are accepted. Please upload a .pdf document.")

        # Check size (Max 5MB)
        if file.size > 5 * 1024 * 1024:
            raise forms.ValidationError("File size exceeds 5MB. Please upload a smaller PDF.")

        return file
