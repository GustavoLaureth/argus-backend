from dateutil.relativedelta import relativedelta
from django.utils import timezone

def get_next_reset_date(profile):
  start = profile.subscription_started_at
  now = timezone.now()

  next_reset = start

  while next_reset <= now:
    next_reset += relativedelta(months=1)

  return next_reset

def get_current_cycle(profile):
  start = profile.subscription_started_at
  now = timezone.now()

  cycle_start = start

  while cycle_start + relativedelta(months=1) <= now:
    cycle_start += relativedelta(months=1)

  cycle_end = cycle_start + relativedelta(months=1)

  return cycle_start, cycle_end