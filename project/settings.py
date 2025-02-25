""",Django settings for project project.

Generated by 'django-admin startproject' using Django 2.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
""",
import os
import itertools
import json

import logging
LOGGER = logging.getLogger(__name__)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
MEDIA_DIR = os.path.join(BASE_DIR, 'media')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '2b%)naz)7da3zhgn7l07l4$04^1^l0#*y#77mv&++-7#w^8&i-'
MAPBOX_TOKEN = 'pk.eyJ1IjoidGhpbmtpbmdyZWVkIiwiYSI6ImNrN2JnODFpMTAzemEzZWxrdjVmMWs1aDgifQ.ilp7OlnOWSrRkVltnP8biQ'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'info.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djangoformsetjs',
    'background_task',
    'gunviolence',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR, ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'


# Database
# thtps://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'antientropy_cs411',
        'USER': 'antientropy_cs411',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'PASSWORD': 'I0t$$Gh#&TYkLniNcedbx4',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'use_unicode': True, 
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [STATIC_DIR, ]

MEDIA_ROOT = MEDIA_DIR
MEDIA_URL = '/media/'

LOGIN_URL = '/userauth/login/'

# Site constant values


def makeChoices(choicelist):
    result = []
    for i in range(len(choicelist)):
        result.append((choicelist[i].lower(), choicelist[i].lower()))
    return result


def makePermutationChoices(choicelist):
    result = []
    for i in range(1, len(choicelist)+1):
        for ele in list(itertools.combinations(choicelist, i)):
            result.append(', '.join(list(ele)))
    return makeChoices(result)


GUNSTOLEN_CHOICES = makeChoices(['Unknown', 'Not-stolen', 'Stolen'])
GENDER_CHOICES = makeChoices(['Male', 'Female'])
HARM_CHOICES = makeChoices(['Killed', 'Injured', 'Unharmed', 'Arrested'])
PTYPE_CHOICES = makeChoices(['Victim', 'Subject-Suspect'])
RELATION_CHOICES = makeChoices([
    'Family',
    'Drive by - Random victims',
    'Aquaintance',
    'Significant others - current or former',
    'Armed Robbery',
    'Gang vs Gang',
    'Mass shooting - Random victims',
    'Mass shooting - Perp Knows Victims',
    'Friends',
    'Neighbor',
    'Co-worker',
    'Home Invasion - Perp Does Not Know Victim',
    'Home Invasion - Perp Knows Victim'
])
AGEGROUP_CHOICES = makeChoices(['Adult 18+', 'Teen 12-17', 'Child 0-11'])
STATE_CHOICES = makeChoices([
    'Alabama',
    'Alaska',
    'Arizona',
    'Arkansas',
    'California',
    'Colorado',
    'Connecticut',
    'Delaware',
    'Florida',
    'Georgia',
    'Hawaii',
    'Idaho',
    'Illinois',
    'Indiana',
    'Iowa',
    'Kansas',
    'Kentucky',
    'Louisiana',
    'Maine',
    'Maryland',
    'Massachusetts',
    'Michigan',
    'Minnesota',
    'Mississippi',
    'Missouri',
    'Montana',
    'Nebraska',
    'Nevada',
    'New Hampshire',
    'New Jersey',
    'New Mexico',
    'New York',
    'North Carolina',
    'North Dakota',
    'Ohio',
    'Oklahoma',
    'Oregon',
    'Pennsylvania',
    'Rhode Island',
    'South Carolina',
    'South Dakota',
    'Tennessee',
    'Texas',
    'Utah',
    'Vermont',
    'Virginia',
    'Washington',
    'West Virginia',
    'Wisconsin',
    'Wyoming',
    'District of Columbia',
    'American Samoa',
    'Guam',
    'Northern Mariana Islands',
    'Puerto Rico',
    'U.S. Virgin Islands',
])
CHARACTER_CHOICES = makeChoices([
    "Shot - Wounded/Injured",
    "Shot - Dead (murder, accidental, suicide)",
    "Shots Fired - No Injuries",
    "Bar/club incident - in or around establishment",
    "Suicide^",
    "Murder/Suicide",
    "Attempted Murder/Suicide (one variable unsuccessful)",
    "Domestic Violence",
    "Mass Shooting (4+ victims injured or killed excluding the subject/suspect/perpetrator, one location)",    "Drive-by (car to street, car to car)",
    "Gang involvement",
    "Home Invasion",
    "Home Invasion - Resident killed",
    "Officer Involved Incident",
    "Officer Involved Shooting - Officer shot",
    "Officer Involved Shooting - Officer killed",
    "Officer Involved Shooting - subject/suspect/perpetrator shot",
    "Officer Involved Shooting - subject/suspect/perpetrator suicide at standoff",
    "Spree Shooting (multiple victims, multiple locations)",
    "Possession of gun by felon or prohibited person",
    "Institution/Group/Business",
    "Officer Involved Shooting - subject/suspect/perpetrator killed",
    "Animal shot/killed",
    "Home Invasion - Resident injured",
    "Drug involvement",
    "Armed robbery with injury/death and/or evidence of DGU found",
    "Mass Murder (4+ deceased victims excluding the subject/suspect/perpetrator , one location)",
    "Concealed Carry License - Perpetrator",
    "Possession (gun(s) found during commission of other crimes)",
    "Stolen/Illegally owned gun{s} recovered during arrest/warrant",
    "School Incident",
    "School Shooting - university/college",
    "Kidnapping/abductions/hostage",
    "Car-jacking",
    "Hate crime",
    "House party",
    "Defensive Use",
    "Defensive Use - Crime occurs, victim shoots subject/suspect/perpetrator",
    "Defensive Use - Victim stops crime",
    "Workplace shooting (disgruntled employee)",
    "Assault weapon (AR-15, AK-47, and ALL variants defined by law enforcement)",
    "Brandishing/flourishing/open carry/lost/found",
    "Non-Shooting Incident",
    "ATF/LE Confiscation/Raid/Arrest",
    "Unlawful purchase/sale",
    "Accidental Shooting",
    "Accidental Shooting - Death",
    "BB/Pellet/Replica gun",
    "Accidental Shooting - Injury",
    "Under the influence of alcohol or drugs (only applies to the subject/suspect/perpetrator )",
    "Accidental/Negligent Discharge",
    "Gun range/gun shop/gun show shooting",
    "Thought gun was unloaded",
    "Child Involved Incident",
    "Child injured self",
    "TSA Action",
    "Road rage",
    "Gun(s) stolen from owner",
    "Home Invasion - No death or injury",
    "School Shooting - elementary/secondary school",
    "Implied Weapon",
    "Officer Involved Shooting - Shots fired, no injury",
    "Accidental Shooting at a Business",
    "Self-Inflicted (not suicide or suicide attempt - NO PERP)",
    "Concealed Carry License - Victim",
    "Criminal act with stolen gun",
    "Suicide - Attempt",
    "Officer Involved Incident - Weapon involved but no shots fired",
    "Gun at school, no death/injury - elementary/secondary school",
    "Gun at school, no death/injury - university/college",
    "Non-Aggression Incident",
    "Home Invasion - subject/suspect/perpetrator injured",
    "Defensive Use - WITHOUT a gun",
    "Cleaning gun",
    "Child picked up & fired gun",
    "Child killed by child",
    "Police Targeted",
    "Home Invasion - subject/suspect/perpetrator killed",
    "Defensive Use - Stand Your Ground/Castle Doctrine established",
    "Hunting accident",
    "Pistol-whipping",
    "Child killed self",
    "Sex crime involving firearm",
    "Playing with gun",
    "Child injured by child",
    "Officer Involved Shooting - subject/suspect/perpetrator unarmed",
    "Shots fired, no action (reported, no evidence found)",
    "ShotSpotter",
    "Defensive Use - Good Samaritan/Third Party",
    "Child killed (not child shooter)",
    "Gun shop robbery or burglary",
    "Shootout (where VENN diagram of shooters and victims overlap)",
    "Guns stolen from law enforcement",
    "Officer Involved Shooting - subject/suspect/perpetrator surrender at standoff",
    "LOCKDOWN/ALERT ONLY: No GV Incident Occurred Onsite",
    "Defensive Use - Shots fired, no injury/death",
    "Defensive use - No shots fired",
    "Officer Involved Shooting - Bystander shot",
    "Officer Involved Shooting - Bystander killed",
    "Child injured (not child shooter)",
    "Gun buy back action",
    "Child with gun - no shots fired",
    "Officer Involved Shooting - Accidental discharge - no injury required",
    "Officer Involved Shooting - subject/suspect/perpetrator suicide by cop",
    "Terrorism Involvement",
    "Ghost gun",
    "Mistaken ID (thought it was an intruder/threat, was friend/family)",
    "Political Violence",
    "NAV"
])

DATE_FORMAT = '%m-%d-%Y'
