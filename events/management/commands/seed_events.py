from django.core.management.base import BaseCommand
from django.utils import timezone
from events.models import Event, Category
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Seed the database with sample events with real images'

    def handle(self, *args, **kwargs):
        Category.objects.all().delete()
        Event.objects.all().delete()

        cats = {
            'Music':   Category.objects.create(name='Music',   icon='🎵', color='#ff6b35'),
            'Comedy':  Category.objects.create(name='Comedy',  icon='😂', color='#fbbf24'),
            'Sports':  Category.objects.create(name='Sports',  icon='⚽', color='#00d4aa'),
            'Tech':    Category.objects.create(name='Tech',    icon='💻', color='#60a5fa'),
            'Art':     Category.objects.create(name='Art',     icon='🎨', color='#a855f7'),
            'Food':    Category.objects.create(name='Food',    icon='🍜', color='#f87171'),
        }

        events_data = [
            # title, category, venue, city, days_ahead, price, total, booked, featured, image_url
            ('Coldplay: Music of the Spheres', 'Music', 'DY Patil Stadium', 'Mumbai', 3, 2500, 15000, 12000, True,
             'https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?w=800&q=80'),
            ('Sunburn Festival 2026', 'Music', 'Vagator Beach', 'Goa', 20, 3500, 10000, 6000, True,
             'https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=800&q=80'),
            ('AR Rahman Live in Concert', 'Music', 'NSCI Dome', 'Mumbai', 35, 1800, 8000, 5200, False,
             'https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=800&q=80'),
            ('Netflix Comedy Gala Night', 'Comedy', 'Chowdiah Memorial Hall', 'Bengaluru', 5, 800, 500, 200, True,
             'https://images.unsplash.com/photo-1527224857830-43a7acc85260?w=800&q=80'),
            ('Zakir Khan Stand-Up Special', 'Comedy', 'Siri Fort Auditorium', 'Delhi', 22, 1200, 1000, 990, False,
             'https://images.unsplash.com/photo-1585699324551-f6c309eedeca?w=800&q=80'),
            ('IPL Playoff: Final Night', 'Sports', 'M. Chinnaswamy Stadium', 'Bengaluru', 7, 600, 40000, 39000, True,
             'https://images.unsplash.com/photo-1540747913346-19212a4b3aad?w=800&q=80'),
            ('Pro Kabaddi League Finals', 'Sports', 'Sardar Patel Sports Complex', 'Ahmedabad', 14, 400, 20000, 12000, False,
             'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&q=80'),
            ('Google Cloud Next India', 'Tech', 'HICC Convention Centre', 'Hyderabad', 10, 2000, 3000, 1500, False,
             'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=800&q=80'),
            ('PyConf India 2026', 'Tech', 'NIMHANS Convention Centre', 'Bengaluru', 25, 1500, 800, 300, False,
             'https://images.unsplash.com/photo-1517180102446-f3ece451e9d8?w=800&q=80'),
            ('Kochi Art Biennale Opening', 'Art', 'Aspinwall House', 'Kochi', 12, 300, 2000, 800, False,
             'https://images.unsplash.com/photo-1561214115-f2f134cc4912?w=800&q=80'),
            ('India Art Fair 2026', 'Art', 'NSIC Exhibition Grounds', 'Delhi', 18, 500, 5000, 3000, False,
             'https://images.unsplash.com/photo-1578301978018-3005759f48f7?w=800&q=80'),
            ('Delhi Street Food Festival', 'Food', 'Jawaharlal Nehru Stadium', 'Delhi', 15, 500, 5000, 3200, False,
             'https://images.unsplash.com/photo-1533777857889-4be7c70b33f7?w=800&q=80'),
            ('Mumbai Food & Wine Expo', 'Food', 'Bandra Kurla Complex', 'Mumbai', 28, 700, 3000, 2100, False,
             'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&q=80'),
        ]

        for title, cat_name, venue, city, days, price, total, booked, featured, img in events_data:
            Event.objects.create(
                title=title,
                description=(
                    f'Experience the incredible {title} — one of the most anticipated events of 2026. '
                    f'Happening live at {venue} in {city}, this is an unmissable experience. '
                    f'Grab your tickets now before they sell out!'
                ),
                category=cats[cat_name],
                venue=venue, city=city,
                date=timezone.now() + timedelta(days=days, hours=random.randint(10, 20)),
                image_url=img,
                total_seats=total, booked_seats=booked,
                price=price, is_featured=featured,
            )

        self.stdout.write(self.style.SUCCESS(f'✅ Seeded {len(events_data)} events!'))
