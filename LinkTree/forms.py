from django import forms

class Form(forms.Form):
    url = forms.URLField(label='URL')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['url'].widget.attrs['class'] = 'form-control'
        self.fields['url'].widget.attrs['placeholder'] = 'URLを入力してください'
