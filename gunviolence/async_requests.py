import asyncio
import pandas as pd
from django.db.models import Sum, F, Q
from django.conf import settings
import re, os, json
from .models import *
from .utils import *
from collections import Counter
import datetime

common_words = [
            "the", "be", "a", "an", "and", "of", "to", "in", "am", "is", "are",
            "at", "not", "that", "have", "i", "it", "for", "on", "with", "he",
            "she", "as", "you", "do", "this", "but", "his", "by", "from",
            "they", "we", "her", "or", "will", "my", "one", "all", "s", "if",
            "any", "our", "may", "your", "these", "d", " ", "me", "so", "what",
            "him", "their", "no", "other", "during", "open", "lost", "found", "non",
            "use", "without", "found"
        ]

async def __requestKilledEachState(date_form):
    total_killed = list(filterGunViolenceEmptyData()\
        .filter(date__range=[date_form.cleaned_data['from_date'], date_form.cleaned_data['to_date']])\
        .values('date', 'state').annotate(n_killed=Sum(F('n_killed'))))
    df = pd.DataFrame(total_killed, columns=['date','state', 'n_killed'])
    fpath = os.path.join(settings.MEDIA_DIR, "n_killed.csv")
    df = df.pivot_table(values='n_killed', index='date', columns = 'state', aggfunc='sum', fill_value=0.0)
    df.to_csv(fpath)

async def __requestInjuredEachState(date_form):
    total_killed = list(filterGunViolenceEmptyData()\
        .filter(date__range=[date_form.cleaned_data['from_date'], date_form.cleaned_data['to_date']])\
        .values('date', 'state').annotate(n_injured=Sum(F('n_injured'))))
    df = pd.DataFrame(total_killed, columns=['date','state', 'n_injured'])
    fpath = os.path.join(settings.MEDIA_DIR, "n_injured.csv")
    df = df.pivot_table(values='n_injured', index='date', columns = 'state', aggfunc='sum', fill_value=0.0)
    df.to_csv(fpath)

async def __requestHarmedEachState(date_form):
    total_killed = list(filterGunViolenceEmptyData()\
        .filter(date__range=[date_form.cleaned_data['from_date'], date_form.cleaned_data['to_date']])\
        .values('date', 'state').annotate(n_harmed=Sum(F('n_injured') + F('n_killed'))))
    df = pd.DataFrame(total_killed, columns=['date','state', 'n_harmed'])
    fpath = os.path.join(settings.MEDIA_DIR, "n_harmed.csv")
    df = df.pivot_table(values='n_harmed', index='date', columns = 'state', aggfunc='sum', fill_value=0.0)
    df.to_csv(fpath)

async def __requestCharactristicWords(date_form):
    rows = list(filterGunViolenceEmptyData()\
        .filter(date__range=[date_form.cleaned_data['from_date'], date_form.cleaned_data['to_date']])\
        .exclude(characteristics="[]")\
        .filter(characteristics__isnull=False)\
        .values('characteristics', 'state').all())
    
    data = []
    for row in rows:
        ch = json.loads(row['characteristics'])
        state = row['state']
        words = []
        for c in ch:
            s = re.split("[^a-zA-Z-]", c['characteristic'].lower())
            for w in s: 
                w = w.strip()
                if len(w) > 0 and not w in common_words and w != '-':
                    words.append(w)
        counter = Counter(words)
        for word, count in dict(counter).items():
            data.append({'state':state, 'word':word, 'size':count})
    fpath = os.path.join(settings.MEDIA_DIR, "characteristics.csv")
    df = pd.DataFrame(data)
    #df = df.pivot_table(values='size', index='date', columns = 'state', aggfunc='sum', fill_value=0.0)
    df.to_csv(fpath, index = False)

async def __requestParticipantAge(date_form):
    rows = list(Participant.objects\
        .filter(incident__date__range=(date_form.cleaned_data['from_date'], date_form.cleaned_data['to_date']))\
        .filter(age__isnull=False)\
        .values('incident__state', 'age')
        .all()
        )
    fpath = os.path.join(settings.MEDIA_DIR, "participant_age.csv")
    df = pd.DataFrame(rows)
    df.to_csv(fpath, index = False)

async def scheduleAsyncRequests(date_form):
    tasks = []
    tasks.append(__requestKilledEachState(date_form))
    tasks.append(__requestInjuredEachState(date_form))
    tasks.append(__requestHarmedEachState(date_form))
    tasks.append(__requestCharactristicWords(date_form))
    tasks.append(__requestParticipantAge(date_form))

    await asyncio.gather(*tasks)
