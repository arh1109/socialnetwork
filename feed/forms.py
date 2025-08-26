# feed/forms.py
from django import forms

class MultiFileInput(forms.ClearableFileInput):
    # Opt-in to multiple file selection
    allow_multiple_selected = True

class PostCreateForm(forms.Form):
    text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "rows": 2,
            "placeholder": "What's on your mind?",
            "class": "composer-textarea",
        })
    )
    attachments = forms.FileField(
        required=False,
        widget=MultiFileInput(attrs={
            "multiple": True,
            "accept": "image/*,video/*",
        })
    )

    def clean(self):
        cleaned = super().clean()
        text = (cleaned.get("text") or "").strip()
        # IMPORTANT: pull the list of files from self.files
        files = self.files.getlist("attachments")
        if not text and not files:
            raise forms.ValidationError("Write something or add at least one photo/video.")
        return cleaned
