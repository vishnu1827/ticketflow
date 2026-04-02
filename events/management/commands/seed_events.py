from django.core.management.base import BaseCommand
from django.utils import timezone
from events.models import Event, Category
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Seed the database with sample events'

    def handle(self, *args, **kwargs):
        Category.objects.all().delete()
        Event.objects.all().delete()

        categories = [
            Category.objects.create(name='Music', icon='🎵'),
            Category.objects.create(name='Comedy', icon='😂'),
            Category.objects.create(name='Sports', icon='⚽'),
            Category.objects.create(name='Tech', icon='💻'),
            Category.objects.create(name='Art', icon='🎨'),
            Category.objects.create(name='Food', icon='🍜'),
        ]

        events_data = [
            ('Coldplay World Tour 2026', 'Music', 'DY Patil Stadium', 'Mumbai', 3, 2500, 15000, 12000, 'https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=600'),
            ('Netflix Comedy Gala', 'Comedy', 'Chowdiah Memorial Hall', 'Bengaluru', 5, 800, 500, 200, 'https://images.unsplash.com/photo-1527224857830-43a7acc85260?w=600'),
            ('IPL Playoff Night', 'Sports', 'M. Chinnaswamy Stadium', 'Bengaluru', 7, 600, 40000, 39000, 'https://images.unsplash.com/photo-1540747913346-19212a4b3aad?w=600'),
            ('Google Cloud Next India', 'Tech', 'HICC', 'Hyderabad', 10, 2000, 3000, 1500, 'https://images.unsplash.com/photo-1517180102446-f3ece451e9d8?w=600'),
            ('Kochi Art Biennale Opening', 'Art', 'Aspinwall House', 'Kochi', 12, 300, 2000, 800, 'https://images.unsplash.com/photo-1561214115-f2f134cc4912?w=600'),
            ('Delhi Street Food Festival', 'Food', 'Jawaharlal Nehru Stadium', 'Delhi', 15, 500, 5000, 3200, 'https://images.unsplash.com/photo-1533777857889-4be7c70b33f7?w=600'),
            ('Sunburn Festival 2026', 'Music', 'Vagator Beach', 'Goa', 20, 3500, 10000, 6000, 'https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=600'),
            ('Stand Up Special: Zakir Khan', 'Comedy', 'Siri Fort Auditorium', 'Delhi', 22, 1200, 1000, 990, 'https://images.unsplash.com/photo-1585699324551-f6c309eedeca?w=600'),
            ('PyConf India 2026', 'Tech', 'NIMHANS Convention Centre', 'Bengaluru', 25, 1500, 800, 300, 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=600'),
            ('Mumbai Food & Wine Expo', 'Food', 'Bandra Kurla Complex', 'Mumbai', 28, 700, 3000, 2100, 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=600'),
        ]

        for title, cat_name, venue, city, days_ahead, price, total, booked, img in events_data:
            cat = next(c for c in categories if c.name == cat_name)
            Event.objects.create(
                title=title,
                description=f'Experience the incredible {title}. An unforgettable event happening live at {venue} in {city}. Get your tickets before they sell out — this is one event you do not want to miss!',
                category=cat,
                venue=venue,
                city=city,
                date=timezone.now() + timedelta(days=days_ahead, hours=random.randint(10, 20)),
                image_url=img,
                total_seats=total,
                booked_seats=booked,
                price=price,
            )

        self.stdout.write(self.style.SUCCESS(f'✅ Seeded {len(events_data)} events across {len(categories)} categories!'))
