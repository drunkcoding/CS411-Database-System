from django.http import JsonResponse
import pandas as pd
from .utils import filterGunViolenceRawEmptyData
from .models import *
from .forms import *

def stateCountEachDate(request, state):

    date_form = DateRangeForm(request.session.get('date_form'))

    if not date_form.is_valid(): return JsonResponse({})

    count_data = list(
            filterGunViolenceRawEmptyData()\
            .filter(date__range=[date_form.cleaned_data['from_date'], date_form.cleaned_data['to_date']])\
            .filter(state = state)\
            .values("n_killed", "n_injured")
        )
    df = pd.DataFrame(count_data)
    
    return JsonResponse(df.to_dict('list'))