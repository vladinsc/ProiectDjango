import sys
import schedule
import time
import logging
from django.conf import settings
from django.core.management import BaseCommand
from ECommerceSite import tasks

class Command(BaseCommand):
    help = 'Porneste scheduler-ul pentru task-urile programate (Newsletter, etc)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Se initializeaza Scheduler-ul...'))

        #delete useri neconfirmati
        k = getattr(settings, 'SCHEDULER_K_DELETE_MINUTES', 60)
        schedule.every(k).minutes.do(tasks.task_delete_unconfirmed_users)

        #newsletter
        day = getattr(settings, 'SCHEDULER_NEWSLETTER_DAY', 'monday')
        hour = getattr(settings, 'SCHEDULER_NEWSLETTER_HOUR', 10)
        getattr(schedule.every(), day).at(hour).do(tasks.task_newsletter)

        #verificare stoc redus
        m = getattr(settings, 'SCHEDULER_M_MINUTES', 30)
        schedule.every(m).minutes.do(tasks.task_raport_stoc)

        #raport saptamanal
        day2 = getattr(settings, 'SCHEDULER_REPORT_DAY', 'friday')
        hour2 = getattr(settings, 'SCHEDULER_REPORT_HOUR', '18:00')
        getattr(schedule.every(), day2).at(hour2).do(tasks.task_raport_saptamanal)

        #task notificari
        schedule.every().day.at("09:00").do(tasks.task_notificare_profil)

        try:
            self.stdout.write(self.style.SUCCESS('Scheduler pornit cu succes. Apasa Ctrl+C pentru a opri.'))
            while True:
                schedule.run_pending()
                time.sleep(1)

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nScheduler oprit manual.'))
