from django import forms
from schedules.forms import ScheduleForm as BaseScheduleForm


class ScheduleForm(BaseScheduleForm):
    operating_days = forms.MultipleChoiceField(
        choices=BaseScheduleForm._meta.model.DAY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label='Operating Days',
    )

    def __init__(self, *args, **kwargs):
        self.agency = kwargs.pop('agency', None)
        super().__init__(*args, **kwargs)
        if self.agency:
            self.fields['bus'].queryset = self.agency.buses.all()
            self.fields['route'].queryset = self.agency.routes.all()
        if self.instance and self.instance.pk and self.instance.operating_days:
            self.initial['operating_days'] = [str(d) for d in self.instance.operating_days]