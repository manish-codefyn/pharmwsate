import os
import json
import uuid
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.files import File
from django.conf import settings
from medicines.models import Medicine, Category

User = get_user_model()

class Command(BaseCommand):
    help = 'Load medicines from a JSON file'

    def handle(self, *args, **options):
        json_path = os.path.join(settings.BASE_DIR, 'data', 'medicines.json')

        if not os.path.exists(json_path):
            self.stderr.write(f"JSON file not found at {json_path}")
            return

        with open(json_path, 'r') as f:
            data = json.load(f)

        for item in data:
            try:
                # Get or create donor
                donor, _ = User.objects.get_or_create(
                    email=item["donor_email"],
                    defaults={"username": item["donor_email"].split("@")[0], "password": "defaultpass"}
                )

                # Get or create recipient
                recipient = None
                if item.get("recipient_email"):
                    recipient, _ = User.objects.get_or_create(
                        email=item["recipient_email"],
                        defaults={"username": item["recipient_email"].split("@")[0], "password": "defaultpass"}
                    )

                # Get or create category
                category, _ = Category.objects.get_or_create(name=item["category"])

                # Parse expiry date
                expiry_date = datetime.strptime(item["expiry_date"], "%Y-%m-%d").date()

                # Create medicine instance
                medicine = Medicine(
                    name=item["name"],
                    description=item.get("description", ""),
                    category=category,
                    quantity=item["quantity"],
                    expiry_date=expiry_date,
                    donor=donor,
                    recipient=recipient,
                    is_available=item.get("is_available", True),
                )

                # Handle image if provided
                image_path = os.path.join(settings.MEDIA_ROOT, item.get("image", ""))
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as img_file:
                        medicine.image.save(os.path.basename(image_path), File(img_file), save=False)

                # Generate slug
                medicine.slug = slugify(f"{medicine.name}-{uuid.uuid4().hex[:6]}")

                # Save medicine
                medicine.save()

                self.stdout.write(self.style.SUCCESS(f"Successfully added: {medicine.name}"))

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error adding {item.get('name')}: {str(e)}"))
