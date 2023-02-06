from django import forms

class Form(forms.Form):
    url = forms.CharField(label='URL')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['url'].widget.attrs['class'] = 'form-control'
        self.fields['url'].widget.attrs['placeholder'] = 'URLをここに入力してください'
