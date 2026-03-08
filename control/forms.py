"""Forms for the control app.

Use Django forms to validate user input when extending the UI beyond
simple HTML forms. At present, the app uses basic HTML forms directly
in templates, so this module is intentionally minimal. You can add
ModelForm subclasses for Dataset or custom calibration forms here.
"""
from __future__ import annotations

from django import forms


class DatasetForm(forms.Form):
    """Example form for dataset creation.

    Not currently used by the templates but left here as a starting
    point if you wish to add server‑side validation or additional
    fields later.
    """
    name = forms.CharField(max_length=255)
    description = forms.CharField(widget=forms.Textarea, required=False)
